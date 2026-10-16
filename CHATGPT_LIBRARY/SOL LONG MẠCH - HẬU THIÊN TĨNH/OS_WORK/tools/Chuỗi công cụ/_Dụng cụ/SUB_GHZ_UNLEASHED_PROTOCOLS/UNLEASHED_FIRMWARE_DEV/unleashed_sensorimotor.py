#!/usr/bin/env python3
"""SENSORIMOTOR -> five auditable external software logs (not LLM internal signals).

No RF/NFC/RFID payload, password, badge identifier, OTP or raw serial buffer is persisted.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import uuid

CHANNELS = {
    "input": "1_RAW_INPUT_OUTPUT.log",        # BETA / source in + I/O metadata
    "spatial": "2_SPATIAL_VECTOR.log",        # SPACE / device/channel/target geometry metadata
    "gating": "3_LOGPROBS_GATING.log",       # GAMMA / software route decision ONLY
    "state": "4_TEMP_STATE.log",            # ALPHA / observable firmware/device app state
    "chrono": "5_CHRONO_CONTINUOUS.log",     # DELTA / append-only continuity
}
EVENT_KINDS = {"SOURCE_INSPECTED","BUILD_PREFLIGHT","BUILD_RESULT","CRASH_DIAGNOSTIC",
               "RPC_FRAME_DIAGNOSTIC","SERIAL_PORT_OBSERVED","SENSOR_READBACK","APP_EVENT",
               "ROUTING_DECISION","TEST_SIMULATION","SOURCE_POINTER"}
ALLOWED_DETAILS = {"interface","firmware_target","driver","transport","status","error_category",
                   "byte_count","sha256","source_ref","path","device_class","event_count",
                   "tool","board","result","note"}

def canon(obj):return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def hash_event(event):return hashlib.sha256(canon(event).encode('utf-8')).hexdigest()

def read_journal(root:Path):
    path=root/CHANNELS['chrono']
    if not path.exists():return []
    records=[]
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip():records.append(json.loads(line))
    return records

def validate_details(details):
    if not isinstance(details,dict):raise ValueError('details must be object')
    unexpected=set(details)-ALLOWED_DETAILS
    if unexpected:raise ValueError('Disallowed/unreviewed detail keys: '+','.join(sorted(unexpected)))
    if len(canon(details))>3000:raise ValueError('details too large')
    if 'sha256' in details and not (isinstance(details['sha256'],str) and len(details['sha256'])==64):
        raise ValueError('sha256 must be digest')
    return details

def verify(root:Path, *, mirrors=True):
    try:records=read_journal(root)
    except (ValueError,OSError) as e:return {"valid":False,"error":str(e)}
    previous='0'*64
    for i,row in enumerate(records,1):
        event={k:v for k,v in row.items() if k!='hash'}
        if row.get('previous_hash')!=previous or row.get('sequence')!=i or row.get('hash')!=hash_event(event):
            return {"valid":False,"bad_sequence":i}
        if row.get('channel') not in CHANNELS or row.get('kind') not in EVENT_KINDS:
            return {"valid":False,"bad_schema_at":i}
        previous=row['hash']
    if not mirrors:
        return {"valid":True,"events":len(records),"last_hash":previous,"software_logs_only":True,"LLM_internal_state_observed":False}
    for channel,file in CHANNELS.items():
        if channel=='chrono':continue
        expected=[x for x in records if x['channel']==channel]
        p=root/file
        try:actual=[json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()] if p.exists() else []
        except (ValueError,OSError) as e:return {"valid":False,"channel":channel,"error":str(e)}
        if expected!=actual:return {"valid":False,"mirror_mismatch":channel}
    return {"valid":True,"events":len(records),"last_hash":previous,
            "software_logs_only":True,"LLM_internal_state_observed":False}

def rebuild_mirrors(root:Path, apply=False):
    state = verify(root, mirrors=False)
    if not state['valid']:
        raise ValueError('Canonical chrono chain invalid; refusing mirror recovery')
    events=read_journal(root)
    plan={k:sum(x['channel']==k for x in events) for k in CHANNELS if k!='chrono'}
    if apply:
        for channel,file in CHANNELS.items():
            if channel=='chrono':continue
            target=root/file
            new=target.with_name(target.name+'.tmp')
            rows=[canon(x)+'\n' for x in events if x['channel']==channel]
            new.write_text(''.join(rows),encoding='utf-8')
            new.replace(target)
        checked=verify(root)
        if not checked['valid']:raise RuntimeError('mirror reconstruction verification failed')
    return {"mirror_counts":plan,"applied":apply,"canonical_chain_valid":True,"readback_verified":verify(root)['valid'] if apply else None}

def append(root:Path,channel:str,kind:str,details:dict,observation='SIMULATED_TEST'):
    if channel not in CHANNELS:raise ValueError('unknown channel')
    if kind not in EVENT_KINDS:raise ValueError('unknown event kind')
    if observation not in ('SIMULATED_TEST','SOURCE_READBACK','DEVICE_READBACK','OPERATOR_REPORTED'):
        raise ValueError('invalid observation provenance')
    validate_details(details)
    root.mkdir(parents=True,exist_ok=True)
    pre=verify(root)
    if not pre['valid']:raise ValueError('existing journal does not verify; refusing to append')
    previous=pre['last_hash']
    event={"schema":"SOL_SENSORIMOTOR_FIVE_LOGS/1.0", "event_id":uuid.uuid4().hex,
           "sequence":pre['events']+1,"timestamp_utc":datetime.now(timezone.utc).isoformat(),
           "channel":channel,"kind":kind,"observation":observation,
           "details":details,"previous_hash":previous}
    event['hash']=hash_event(event)
    line=canon(event)+'\n'
    # Chrono log acts as the event source; channel file is a derived mirror.
    with (root/CHANNELS['chrono']).open('a',encoding='utf-8') as f:
        f.write(line); f.flush()
    if channel!='chrono':
        with (root/CHANNELS[channel]).open('a',encoding='utf-8') as f:
            f.write(line);f.flush()
    result=verify(root)
    if not result['valid']:raise RuntimeError('post-write journal verification failed')
    return {"event_id":event['event_id'],"sequence":event['sequence'],
            "hash":event['hash'],"readback_verified":True,"channel":channel}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--logs-dir',type=Path,required=True)
    cmds=p.add_subparsers(dest='cmd',required=True)
    r=cmds.add_parser('record');r.add_argument('--channel',choices=CHANNELS.keys(),required=True)
    r.add_argument('--kind',choices=sorted(EVENT_KINDS),required=True)
    r.add_argument('--observation',choices=['SIMULATED_TEST','SOURCE_READBACK','DEVICE_READBACK','OPERATOR_REPORTED'],default='SIMULATED_TEST')
    r.add_argument('--details-json',required=True)
    cmds.add_parser('verify')
    repair=cmds.add_parser('rebuild-mirrors'); repair.add_argument('--apply',action='store_true')
    a=p.parse_args()
    try:
        if a.cmd=='verify':result=verify(a.logs_dir)
        elif a.cmd=='rebuild-mirrors':result=rebuild_mirrors(a.logs_dir,a.apply)
        else:result=append(a.logs_dir,a.channel,a.kind,json.loads(a.details_json),a.observation)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0 if result.get('valid',result.get('readback_verified',result.get('canonical_chain_valid',False))) else 2
    except (ValueError,OSError,RuntimeError) as e:
        print(json.dumps({"error":str(e)}),file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())
