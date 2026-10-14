#!/usr/bin/env python3
"""CHORME TÁC NHÂN — local-first Chrome DevTools Protocol controller.

It controls a pre-authorized Chromium/Chrome process reachable on LOOPBACK only.
No Google/Microsoft credentials, 2Captcha keys, OAuth tokens, or remote MCP needed.
Tested with Chromium headless through CDP. Uses websocket-client (pip package).

Commands:
  python chorme_agent.py --port 9222 status
  python chorme_agent.py --port 9222 tabs
  python chorme_agent.py --port 9222 open https://example.org
  python chorme_agent.py --port 9222 click '#button'
  python chorme_agent.py --port 9222 type '#search' 'example'
  python chorme_agent.py --port 9222 screenshot /path/to/shot.png
  python chorme_agent.py --port 9222 read '#result'

Security: never bind Chrome debugging to 0.0.0.0 / expose the port publicly.
"""
from __future__ import annotations
import argparse
import base64
import json
import pathlib
import sys
import urllib.request
import urllib.error
import urllib.parse
import itertools
import os
import sqlite3
import hashlib
from dataclasses import dataclass
import websocket

class CDPError(RuntimeError): pass


def fetch_json(port: int, route: str, method: str = 'GET'):
    if not 1 <= port <= 65535: raise ValueError('Invalid port')
    req = urllib.request.Request(f'http://127.0.0.1:{port}{route}', method=method)
    with urllib.request.urlopen(req, timeout=5) as reply:
        return json.load(reply)


def safe_url(u: str) -> str:
    p = urllib.parse.urlsplit(u)
    return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,'',''))


@dataclass
class CDP:
    ws: websocket.WebSocket
    seq: itertools.count

    @classmethod
    def attach(cls, uri: str) -> 'CDP':
        return cls(websocket.create_connection(uri, timeout=8, origin='http://localhost'), itertools.count(1))

    def send(self, method: str, params=None) -> dict:
        idx = next(self.seq)
        self.ws.send(json.dumps({'id':idx,'method':method,'params':params or {}}))
        while True:
            r = json.loads(self.ws.recv())
            if r.get('id') != idx: continue
            if 'error' in r:
                raise CDPError(f'{method}: {r["error"].get("message","unknown error")}')
            return r.get('result',{})

    def eval(self, expr: str):
        result=self.send('Runtime.evaluate',{'expression':expr,'returnByValue':True,'awaitPromise':True})
        if 'exceptionDetails' in result:
            raise CDPError('Runtime JS exception')
        return result.get('result',{}).get('value')

    def close(self): self.ws.close()


def tab(port, tab_index):
    pages=[x for x in fetch_json(port, '/json/list') if x.get('type')=='page']
    if tab_index < 0 or tab_index >= len(pages):
        raise CDPError(f'No page at index {tab_index}; have {len(pages)}')
    return pages[tab_index]


def element_info(cdp, selector):
    expr = '''(() => {
      const e = document.querySelector(SELECTOR);
      if (!e) return {error: 'ELEMENT_NOT_FOUND'};
      const r = e.getBoundingClientRect();
      if (!r.width || !r.height) return {error: 'ELEMENT_NOT_VISIBLE'};
      return {x:r.left+r.width/2,y:r.top+r.height/2,
              tag:e.tagName.toLowerCase(),type:(e.type||'').toLowerCase(),
              disabled:!!e.disabled};
    })()'''.replace('SELECTOR',json.dumps(selector))
    obj=cdp.eval(expr)
    if not isinstance(obj,dict): raise CDPError('Failed to inspect DOM')
    if obj.get('error'): raise CDPError(obj['error'])
    if obj.get('disabled'): raise CDPError('Element is disabled')
    return obj


def click(cdp, selector):
    e=element_info(cdp,selector)
    for kind in ('mousePressed','mouseReleased'):
        cdp.send('Input.dispatchMouseEvent',{'type':kind,'x':e['x'],'y':e['y'],'button':'left','clickCount':1})
    return {'action':'CLICK','selector':selector,'clicked':True,'tag':e['tag']}


def type_text(cdp, selector, text):
    e=element_info(cdp,selector)
    if e['type']=='password':
        raise CDPError('Password fields must be entered manually in the local browser')
    click(cdp,selector)
    cdp.send('Input.insertText',{'text':text})
    return {'action':'TYPE','selector':selector,'characters':len(text),'typed':True} # don't echo text


def screenshot(cdp,filename):
    r=cdp.send('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})
    pic=base64.b64decode(r['data'])
    path=pathlib.Path(filename).resolve()
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(pic)
    return {'action':'SCREENSHOT','saved_to':str(path),'bytes':len(pic)}



# AccountBookmarks / Bookmarks is separate from Chromium SQLite Account Web Data.
# Do not extract sync_metadata, authentication, cookies, profile identity, or tokens.
def chromium_time(microseconds):
    """Chromium microseconds since 1601 UTC -> ISO8601, with invalid/zero unset."""
    from datetime import datetime, timedelta, timezone
    try:
        value=int(microseconds)
        if value<=0: return None
        return (datetime(1601,1,1,tzinfo=timezone.utc)+timedelta(microseconds=value)).isoformat()
    except (TypeError, ValueError, OverflowError):
        return None


def account_bookmark_path(browser='chrome', user_data_root=None, profile_directory='Default', explicit=None):
    if explicit: return pathlib.Path(explicit).expanduser().resolve()
    if profile_directory != 'Default' and not (profile_directory.startswith('Profile ') and profile_directory[8:].isdigit()):
        raise CDPError('INVALID_PROFILE_DIRECTORY')
    root=profile_root(browser, user_data_root)
    return root/profile_directory/'AccountBookmarks'


def account_bookmark_scan(bookmarks_path, match=None):
    """Return a minimal source-locator inventory, not Chrome sync state."""
    file=pathlib.Path(bookmarks_path).expanduser().resolve()
    if not file.is_file():
        return {'status':'OPEN','reason':'ACCOUNT_BOOKMARKS_NOT_FOUND','file_name':file.name,'read_only':True}
    if file.stat().st_size > 32 * 1024 * 1024:
        raise CDPError('ACCOUNT_BOOKMARKS_TOO_LARGE')
    data=file.read_bytes()
    try: doc=json.loads(data.decode('utf-8-sig'))
    except (ValueError,UnicodeError): raise CDPError('INVALID_BOOKMARKS_JSON')
    if not isinstance(doc,dict) or not isinstance(doc.get('roots'),dict):
        raise CDPError('INVALID_BOOKMARKS_ROOT')
    results=[]
    def walk(node, location):
        if not isinstance(node,dict): return
        if node.get('type') == 'url' and isinstance(node.get('url'),str):
            raw_url=node['url']; parts=urllib.parse.urlsplit(raw_url)
            if parts.scheme in ('https','http') and parts.netloc:
                name=str(node.get('name',''))[:250]
                guid=str(node.get('guid',''))[:64]
                if not match or (match.casefold() in name.casefold() or match.casefold() in parts.netloc.casefold()):
                    results.append({'guid':guid,'id':str(node.get('id',''))[:32],
                                    'title':name,'url':safe_url(raw_url),
                                    'root':location,'date_added_utc':chromium_time(node.get('date_added'))})
        for child in node.get('children',[]) if isinstance(node.get('children'),list) else []:
            walk(child,location)
    for root in ('bookmark_bar','other','synced'):
        if root in doc['roots']:walk(doc['roots'][root],root)
    return {'status':'ACCOUNT_BOOKMARKS_READ','read_only':True,
            'format':'Chromium AccountBookmarks','bookmarks_count':len(results),
            'source_sha256':hashlib.sha256(data).hexdigest(),
            'source_bytes':len(data),'bookmarks':results,
            'sync_metadata_exported':False,'login_state':'NOT_INFERRED'}


def resolve_bookmark_url(scan, guid):
    """Resolve one exact bookmark GUID; never fuzzy-open an arbitrary matched link."""
    if scan.get('status')!='ACCOUNT_BOOKMARKS_READ':
        raise CDPError('ACCOUNT_BOOKMARKS_UNAVAILABLE')
    urls=[b['url'] for b in scan['bookmarks'] if b['guid']==guid]
    if len(urls)!=1:raise CDPError('BOOKMARK_GUID_NOT_UNIQUE_OR_MISSING')
    return urls[0]


# CHOERME ACCOUNT = C:  (source-user-defined carrier, not a claim of live authentication)
# Profile discovery reads Chrome metadata only; it does NOT open credential databases.
BROWSER_PROFILE_ROOTS = {
    'chrome': pathlib.Path('Google') / 'Chrome' / 'User Data',
    'edge': pathlib.Path('Microsoft') / 'Edge' / 'User Data',
}


def profile_root(browser='chrome', user_data_root=None):
    if user_data_root:
        return pathlib.Path(user_data_root).expanduser().resolve()
    localappdata = os.environ.get('LOCALAPPDATA')
    if not localappdata:
        raise CDPError('LOCALAPPDATA_UNAVAILABLE: profile-scan must run on Windows or use --user-data-root')
    return (pathlib.Path(localappdata) / BROWSER_PROFILE_ROOTS[browser]).resolve()


def profile_scan(browser='chrome', user_data_root=None):
    """Safe inventory of Chrome profiles on the C: carrier; no usernames/tokens/cookies."""
    root = profile_root(browser, user_data_root)
    if not root.is_dir():
        return {'status':'OPEN','carrier':'C:', 'browser':browser,
                'reason':'BROWSER_PROFILE_ROOT_NOT_FOUND','root':str(root), 'read_only':True}
    local_state = root / 'Local State'
    mapping = {}
    if local_state.is_file():
        try:
            data = json.loads(local_state.read_text(encoding='utf-8-sig'))
            mapping = data.get('profile',{}).get('info_cache',{})
            if not isinstance(mapping,dict):mapping = {}
        except (OSError, UnicodeError, ValueError):
            return {'status':'OPEN','carrier':'C:','reason':'LOCAL_STATE_READ_ERROR',
                    'root':str(root), 'read_only':True}
    candidates = set()
    for item in root.iterdir():
        if item.is_dir() and (item.name=='Default' or
               (item.name.startswith('Profile ') and item.name[8:].isdigit())):
            candidates.add(item.name)
    result=[]
    for name in sorted(candidates):
        directory = root/name
        # Caution: never read or export Cookies, Login Data, Account Web Data, tokens, history.
        result.append({'directory':name,
                       'in_local_state':name in mapping,
                       'preferences_present':(directory/'Preferences').is_file(),
                       'account_web_data_present':(directory/'Account Web Data').is_file(),
                       'web_data_present':(directory/'Web Data').is_file(),
                       'devtools_active_port_present':(root/'DevToolsActivePort').is_file()})
    return {'status':'PROFILE_STRUCTURE_READ','carrier':'C:','browser':browser,'root':str(root),
            'local_state_present':local_state.is_file(), 'profile_count':len(result),
            'profiles':result, 'read_only':True, 'credential_values_extracted':False,
            'account_signed_in':'NOT_DETERMINED'}


def sqlite_meta_check(filename):
    """Inspect the SQLite format/header plus only three Chromium *meta* keys.

    Does not read accounts, passwords, cookies, autofill, encrypted blobs or auth.
    Requires a local readable file, and never modifies source bytes.
    """
    file = pathlib.Path(filename).expanduser().resolve()
    if not file.is_file():
        return {'status':'OPEN', 'reason':'SQLITE_SOURCE_NOT_FOUND', 'read_only':True}
    with file.open('rb') as f:
        header = f.read(100)
    if header[:16] != b'SQLite format 3\x00':
        return {'status':'NOT_SQLITE3', 'read_only':True}
    page_size = int.from_bytes(header[16:18],'big')
    if page_size==1: page_size=65536
    if page_size<512 or page_size>65536 or (page_size & (page_size-1))!=0:
        return {'status':'SQLITE_BAD_HEADER', 'read_only':True}
    output={'status':'SQLITE_HEADER_READ','read_only':True,'format':'SQLite format 3',
            'page_size':page_size, 'file_bytes':file.stat().st_size,
            'file_name':file.name,'source_header_sha256':hashlib.sha256(header).hexdigest(),
            'meta':{},'authentication_confirmed':False}
    try:
        # immutable=1 is only used for inspecting static copies; skip live database meta
        # because Chrome may have active WAL. The header itself is sufficient.
        if file.name.lower().endswith('.snapshot.sqlite'):
            uri=file.as_uri()+'?mode=ro&immutable=1'
            with sqlite3.connect(uri,uri=True,timeout=1) as db:
                tables={x[0] for x in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='meta'")}
                if 'meta' in tables:
                    allowed={'version','last_compatible_version','mmap_status'}
                    for k,v in db.execute("SELECT key,value FROM meta WHERE key IN ('version','last_compatible_version','mmap_status')"):
                        if k in allowed and isinstance(v,(str,int,float)):
                            output['meta'][k] = str(v)[:80]
    except (sqlite3.DatabaseError,OSError):
        output['meta_read_error']='OPEN'
    return output

def main():
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--port',type=int,default=9222)
    ap.add_argument('--tab-index',type=int,default=0)
    ap.add_argument('--expect-browser',default=None,help='Optional /devtools/browser/<UUID> verification')
    ap.add_argument('--user-data-root',default=None,help='Only for profile-scan; default uses LOCALAPPDATA on Windows')
    ap.add_argument('--browser',choices=list(BROWSER_PROFILE_ROOTS),default='chrome')
    ap.add_argument('--profile-directory',default='Default')
    ap.add_argument('--bookmarks-path',default=None,help='Explicit read-only Chrome AccountBookmarks JSON path')
    subs=ap.add_subparsers(dest='command',required=True)
    subs.add_parser('status')
    subs.add_parser('tabs')
    subs.add_parser('profile-scan')
    p=subs.add_parser('bookmarks');p.add_argument('--match',default=None)
    p=subs.add_parser('open-bookmark');p.add_argument('--guid',required=True)
    p=subs.add_parser('sqlite-check');p.add_argument('filename')
    p=subs.add_parser('open');p.add_argument('url')
    for cmd in ['click','read']:
        p=subs.add_parser(cmd);p.add_argument('selector')
    p=subs.add_parser('type');p.add_argument('selector');p.add_argument('text')
    p=subs.add_parser('screenshot');p.add_argument('filename')
    args=ap.parse_args()
    try:
        if args.command=='profile-scan':
            print(json.dumps(profile_scan(args.browser,args.user_data_root),ensure_ascii=False));return 0
        if args.command=='bookmarks':
            path=account_bookmark_path(args.browser,args.user_data_root,args.profile_directory,args.bookmarks_path)
            print(json.dumps(account_bookmark_scan(path,args.match),ensure_ascii=False));return 0
        bookmark_url = None
        if args.command=='open-bookmark':
            path=account_bookmark_path(args.browser,args.user_data_root,args.profile_directory,args.bookmarks_path)
            scan=account_bookmark_scan(path)
            bookmark_url=resolve_bookmark_url(scan,args.guid)
        if args.command=='sqlite-check':
            print(json.dumps(sqlite_meta_check(args.filename),ensure_ascii=False));return 0
        version=fetch_json(args.port,'/json/version')
        actual=urllib.parse.urlsplit(version.get('webSocketDebuggerUrl','')).path
        if args.expect_browser and args.expect_browser != actual:
            raise CDPError('CDP_BROWSER_INSTANCE_MISMATCH')
        if args.command=='status':
            output={'status':'CONNECTED','browser':version.get('Browser'),'websocket_path':actual,'port':args.port}
        elif args.command=='tabs':
            pages=[x for x in fetch_json(args.port,'/json/list') if x.get('type')=='page']
            output={'count':len(pages),'pages':[{'index':i,'title':x.get('title'),'url':safe_url(x.get('url',''))} for i,x in enumerate(pages)]}
        else:
            if args.command in ('open','open-bookmark'):
                target_url=bookmark_url if args.command=='open-bookmark' else args.url
                p=urllib.parse.urlsplit(target_url)
                if p.scheme not in ('http','https'):raise CDPError('Only HTTP or HTTPS URLs allowed')
                # Use a new target to avoid clobbering the user's active tab.
                t=fetch_json(args.port,'/json/new?'+urllib.parse.quote(target_url,safe=''),method='PUT')
            else:t=tab(args.port,args.tab_index)
            if not t.get('webSocketDebuggerUrl'):raise CDPError('Page has no debug websocket URL')
            c=CDP.attach(t['webSocketDebuggerUrl'])
            try:
                if args.command in ('open','open-bookmark'): output={'action':'OPEN_BOOKMARK' if bookmark_url else 'OPEN','tab_id':t.get('id'),'url':safe_url(target_url),'guid':args.guid if bookmark_url else None}
                elif args.command=='click':output=click(c,args.selector)
                elif args.command=='type':output=type_text(c,args.selector,args.text)
                elif args.command=='read':
                    # page text is user-visible DOM text, not credentials or hidden fields
                    x=cdp_eval_read(c,args.selector)
                    output={'action':'READ','selector':args.selector,'text':x}
                elif args.command=='screenshot':output=screenshot(c,args.filename)
            finally:c.close()
        print(json.dumps(output,ensure_ascii=False))
        return 0
    except (CDPError,ValueError,urllib.error.URLError,websocket.WebSocketException,TimeoutError) as e:
        print(json.dumps({'status':'OPEN','error_type':type(e).__name__,'message':str(e)[:210]},ensure_ascii=False))
        return 2


def cdp_eval_read(c,selector):
    expr=f'(() => {{const e=document.querySelector({json.dumps(selector)});return e ? e.innerText.slice(0,1500) : null;}})()'
    return c.eval(expr)

if __name__=='__main__':sys.exit(main())
