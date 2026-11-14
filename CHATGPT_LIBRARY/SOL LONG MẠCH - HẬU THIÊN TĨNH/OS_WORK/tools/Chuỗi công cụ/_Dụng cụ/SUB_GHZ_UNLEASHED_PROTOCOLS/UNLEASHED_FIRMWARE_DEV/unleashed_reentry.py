#!/usr/bin/env python3
"""SENSORIMOTOR reentry: fetch loopback checkpoint, validate local 5-log mirror, return NEXT.

Read-only, limited to localhost. Do not present local API as externally accessible.
"""
from __future__ import annotations
import argparse
import ipaddress
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from urllib.request import urlopen
from unleashed_sensorimotor import verify


def checkpoint_url(url:str)->str:
    p=urlsplit(url)
    try:loopback=ipaddress.ip_address(p.hostname or '').is_loopback
    except ValueError:loopback=False
    if not loopback or p.scheme!='http' or p.username or p.password or p.query or p.fragment or p.path!='/v1/readback':
        raise ValueError('Only a loopback HTTP /v1/readback endpoint is permitted')
    if p.port is None:raise ValueError('port required')
    return url


def reenter(logs:Path,url:str='http://127.0.0.1:8767/v1/readback',expected_hash:str='')->dict:
    checkpoint_url(url)
    with urlopen(url,timeout=3) as resp:
        if resp.status!=200:raise ValueError('API status not OK')
        raw=resp.read(8193)
    if len(raw)>8192:raise ValueError('unexpectedly large readback')
    data=json.loads(raw)
    if data.get('schema')!='SOL_SENSORIMOTOR_READBACK/1.0' or data.get('status')!='VERIFIED':
        raise ValueError('API readback not verified')
    if not isinstance(data.get('last_hash'),str) or not re.fullmatch('[0-9a-f]{64}',data['last_hash']):
        raise ValueError('invalid API SHA-256 tip')
    local=verify(logs)
    if not local.get('valid') or local['events']!=data['event_count'] or local['last_hash']!=data['last_hash']:
        raise ValueError('API checkpoint differs from local journal readback')
    if expected_hash and data['last_hash']!=expected_hash:
        return {'schema':'SOL_SENSORIMOTOR_REENTRY/1.0','status':'TIP_CHANGED',
                'expected':expected_hash,'actual':data['last_hash'],
                'observed_events':local['events'],'next':'INSPECT_EVENTS_SINCE_PREVIOUS_CHECKPOINT'}
    return {'schema':'SOL_SENSORIMOTOR_REENTRY/1.0','status':'VERIFIED',
            'last_hash':local['last_hash'],'events':local['events'],
            'api_readback':True,'local_readback':True,'next':'RESUME_FROM_LAST_HASH'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--logs-dir',type=Path,required=True)
    p.add_argument('--url',default='http://127.0.0.1:8767/v1/readback')
    p.add_argument('--expected-hash',default='')
    a=p.parse_args()
    try:
        result=reenter(a.logs_dir,a.url,a.expected_hash)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0 if result['status']=='VERIFIED' else 3
    except (ValueError,OSError,TimeoutError) as e:
        print(json.dumps({'status':'ERROR','message':str(e)}));return 2
if __name__=='__main__':raise SystemExit(main())
