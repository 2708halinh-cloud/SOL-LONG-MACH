#!/usr/bin/env python3
"""Read-only local check for user's existing HOME_SOL sandbox API, no daemon startup."""
from __future__ import annotations
import json, pathlib, sys, urllib.error, urllib.request, urllib.parse, webbrowser

CONFIG = pathlib.Path(__file__).with_name('HOME_SOL_Sandbox.json')
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise RuntimeError('Redirect not allowed')

def validate_config():
    config=json.loads(CONFIG.read_text(encoding='utf-8'))
    endpoints={'http://127.0.0.1:8765/sandbox/sol','http://127.0.0.1:8765/api/devices'}
    if set(config['allowed_urls']) != endpoints or config['method']!='GET':
        raise ValueError('Unexpected endpoints/method: only specified localhost destinations allowed')
    for url in endpoints:
        p=urllib.parse.urlsplit(url)
        if (p.scheme,p.hostname,p.port) != ('http','127.0.0.1',8765):
            raise ValueError('Only localhost port 8765 may be accessed')
    return config

def check_device(config):
    request=urllib.request.Request(config['devices_api_url'],headers={'Accept':'application/json'},method='GET')
    with urllib.request.build_opener(NoRedirect()).open(request,timeout=5) as r:
        if r.status != 200: raise RuntimeError('API HTTP '+str(r.status))
        data=r.read(2_000_001)
    if len(data)>2_000_000: raise RuntimeError('response too large')
    obj=json.loads(data.decode('utf-8'))
    if obj.get('schema') != config['expected_api_schema']: raise RuntimeError('Unexpected schema')
    if obj.get('host') != config['host']: raise RuntimeError('Unexpected host')
    c=obj.get('modules',{}).get('hostComputer',{}).get('drives',[])
    drive=next((x for x in c if x.get('letter','').upper()=='C:'),None)
    gpu=obj.get('modules',{}).get('hostComputer',{}).get('gpus',[])
    return {'readback':'LIVE_LOCAL_GET_OK','host':obj['host'],'timestamp':obj.get('timestamp'),'disk_c':drive,'gpus':gpu}

def check_sandbox(config):
    req=urllib.request.Request(config['sandbox_url'],headers={'Accept':'text/html,application/json'},method='GET')
    with urllib.request.build_opener(NoRedirect()).open(req,timeout=5) as r:
        code=r.status;content_type=r.headers.get('Content-Type','')
        _=r.read(512)
    return {'readback':'LOCAL_SANDBOX_HTTP_PROBE','url':config['sandbox_url'],'http_status':code,'content_type':content_type}

def main():
    config=validate_config()
    mode=sys.argv[1] if len(sys.argv)>1 else 'devices'
    if mode=='devices': result=check_device(config)
    elif mode=='sandbox': result=check_sandbox(config)
    elif mode=='open':
        result={'url':config['sandbox_url'],'open_requested':webbrowser.open_new_tab(config['sandbox_url'])}
    elif mode=='config': result=config
    else: raise SystemExit('Usage: python home_sol_check.py [devices|sandbox|open|config]')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
