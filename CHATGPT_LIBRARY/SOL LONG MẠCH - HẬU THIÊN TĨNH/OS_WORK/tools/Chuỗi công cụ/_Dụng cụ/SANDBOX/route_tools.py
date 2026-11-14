#!/usr/bin/env python3
"""Read-only local routing registry. This does not emulate connected MCP tools."""
import argparse,json,pathlib,sys
manifest=pathlib.Path(__file__).with_name('ALL_TEN_TOOLS.json')
def main():
 p=argparse.ArgumentParser()
 p.add_argument('cmd',choices=['list','get','check'])
 p.add_argument('alias',nargs='?')
 a=p.parse_args()
 d=json.loads(manifest.read_text(encoding='utf-8'))
 if a.cmd=='check':
  aliases=[x['alias'] for x in d['items']]
  assert len(aliases)==10 and len(set(aliases))==10
  assert all(x['entrypoint'] and x['observed_state'] for x in d['items'])
  assert d['secrets_policy']=='REFERENCE_ONLY_NO_PLAINTEXT'
  print(json.dumps({'PASS':True,'tool_count':len(aliases),'secrets':'opaque_refs_only'},ensure_ascii=False));return
 if a.cmd=='list':
  for x in d['items']:print('%s | %s | %s'%(x['alias'],x['observed_state'],x['entrypoint']))
 else:
  match=[x for x in d['items'] if x['alias']==(a.alias or '').upper()]
  if not match:raise SystemExit('unknown alias; run list')
  print(json.dumps(match[0],indent=2,ensure_ascii=False))
if __name__=='__main__':main()
