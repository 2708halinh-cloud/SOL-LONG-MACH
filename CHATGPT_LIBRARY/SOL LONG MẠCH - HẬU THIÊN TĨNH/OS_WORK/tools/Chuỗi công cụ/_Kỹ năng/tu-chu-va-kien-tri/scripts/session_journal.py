#!/usr/bin/env python3
"""Append-only five-wave event journal, hash chain & restart readback.

This writes *local files only*, never claims ChatGPT runtime interception.
Default content is metadata, not conversation text; caller must redact source.
No network calls, background processes, or automatic permissions.

Example:
 python session_journal.py record --directory ./journal --input event.json
 python session_journal.py verify --directory ./journal
 python session_journal.py resume --directory ./journal
 python session_journal.py --self-test
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import pathlib
import re
import tempfile
from datetime import datetime, timezone

CHANNELS = {
    "BETA": "1_RAW_INPUT_OUTPUT.log",
    "SPACE": "2_SPATIAL_VECTOR.log",
    "GAMMA": "3_LOGPROBS_GATING.log",
    "THETA": "4_TEMP_STATE.log",
    "DELTA": "5_CHRONO_CONTINUOUS.log",
}
SENSITIVE = re.compile(r"(?i)(bearer\s+\S+|sk-[A-Za-z0-9_-]{12,}|AIza[A-Za-z0-9_-]{20,})")
FIELDS = {"event_id", "objective", "event", "source_ref", "provider", "action", "provider_receipt", "readback", "state", "next_agent", "next_user_if_required", "blocker", "space_id", "observed_at", "route_state", "notes"}
ZERO = "0" * 64

def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def sanitized(ev):
    if not isinstance(ev, dict):
        raise ValueError("event must be object")
    if set(ev).difference(FIELDS):
        raise ValueError("unknown event fields")
    if not isinstance(ev.get("event_id"), str) or not (1 <= len(ev["event_id"]) <= 128):
        raise ValueError("event_id is required")
    if not isinstance(ev.get("objective"), str) or not ev["objective"].strip():
        raise ValueError("objective is required")
    for k, v in ev.items():
        if not (v is None or isinstance(v, (str, int, bool))):
            raise ValueError("only scalar event metadata is supported")
        if isinstance(v, str) and (len(v) > 2048 or SENSITIVE.search(v)):
            raise ValueError("sensitive or oversized metadata field")
    return ev

def wave_projections(ev):
    eid=ev['event_id']
    return {
       'BETA': {'event_id':eid,'source_ref':ev.get('source_ref'),'objective':ev['objective']},
       'SPACE':{'event_id':eid,'space_id':ev.get('space_id'),'state': 'NOT_A_SPATIAL_SIGNAL' if not ev.get('space_id') else 'SPACE_ID_OBSERVED'},
       'GAMMA':{'event_id':eid,'route_state':ev.get('route_state'),'logprobs':'NOT_OBSERVED'},
       'THETA':{'event_id':eid,'provider':ev.get('provider'),'provider_receipt':ev.get('provider_receipt'),'readback':ev.get('readback')},
       'DELTA':{'event_id':eid,'observed_at':ev['observed_at'],'state':ev.get('state'),'next_agent':ev.get('next_agent'),'next_user_if_required':ev.get('next_user_if_required')},
    }

def paths(root):
    source=pathlib.Path(root).expanduser()
    if source.is_symlink(): raise ValueError("journal directory symlink refused")
    root=source.resolve()
    root.mkdir(parents=True,exist_ok=True)
    return root, root/'CONTINUITY_EVENTS.jsonl'

def rows(root):
    _, f = paths(root)
    if not f.exists(): return []
    if f.is_symlink(): raise ValueError("journal file symlink refused")
    out=[]
    with f.open('r',encoding='utf-8') as h:
        for i,line in enumerate(h,1):
            try: out.append(json.loads(line))
            except (ValueError,TypeError): raise ValueError(f"invalid journal JSON line {i}")
    return out

def verify(root):
    items=rows(root)
    prev=ZERO
    ids=set()
    for i,item in enumerate(items,1):
        if item.get('schema')!='SOL_SESSION_CONTINUITY/1.0' or item.get('sequence')!=i:
            raise ValueError(f"invalid schema or sequence at {i}")
        if item.get('previous_hash')!=prev: raise ValueError(f"broken chain at {i}")
        eid=item.get('event',{}).get('event_id')
        if eid in ids: raise ValueError(f"duplicate event_id at {i}")
        ids.add(eid)
        body={k:v for k,v in item.items() if k!='hash'}
        sha=hashlib.sha256(canonical(body).encode()).hexdigest()
        if item.get('hash') != sha: raise ValueError(f"broken content hash at {i}")
        prev=sha
    # All five projection files must match the chain before a checkpoint is called valid.
    if items:
        directory=pathlib.Path(root)
        for ch, fn in CHANNELS.items():
            file=directory / fn
            if file.is_symlink() or not file.is_file():
                raise ValueError(f"missing/symlink wave projection: {fn}")
            lines=file.read_text(encoding='utf-8').splitlines()
            if len(lines)!=len(items):
                raise ValueError(f"wave projection count mismatch: {fn}")
            for i,(line,entry) in enumerate(zip(lines,items),1):
                try:proj=json.loads(line)
                except ValueError:raise ValueError(f"invalid projection: {fn}:{i}")
                if proj.get('seq')!=i or proj.get('channel')!=ch or proj.get('event_hash')!=entry['hash'] or proj.get('data')!=wave_projections(entry['event'])[ch]:
                    raise ValueError(f"projection out of sync: {fn}:{i}")
    return {"pass":True,"entries":len(items),"last_hash":prev,"last_event":items[-1]['event'] if items else None}

def record(root, event):
    ev=sanitized(event)
    checked=verify(root)
    _, fp=paths(root)
    if fp.is_symlink(): raise ValueError("journal file symlink refused")
    if any(x['event']['event_id']==ev['event_id'] for x in rows(root)):
        raise ValueError("duplicate event_id")
    if "observed_at" not in ev:
        ev={**ev,"observed_at":datetime.now(timezone.utc).isoformat()}
    body={"schema":"SOL_SESSION_CONTINUITY/1.0","sequence":checked['entries']+1,"previous_hash":checked['last_hash'],"event":ev}
    obj={**body,"hash":hashlib.sha256(canonical(body).encode()).hexdigest()}
    flags=os.O_CREAT|os.O_WRONLY|os.O_APPEND
    if hasattr(os,'O_NOFOLLOW'):flags |= os.O_NOFOLLOW
    fd=os.open(fp,flags,0o600)
    try:
        with os.fdopen(fd,'a',encoding='utf-8') as f:
            f.write(canonical(obj)+'\n'); f.flush(); os.fsync(f.fileno())
    finally:
        pass
    # Derived five-wave readbacks contain only non-secret metadata. These are
    # new local journal files; do not rewrite historical provider files.
    projections=wave_projections(ev)
    d=pathlib.Path(root)
    for ch,fn in CHANNELS.items():
        wf=d/fn
        if wf.is_symlink():raise ValueError('log symlink refused')
        wf_flags=os.O_CREAT|os.O_WRONLY|os.O_APPEND
        if hasattr(os,'O_NOFOLLOW'):wf_flags |= os.O_NOFOLLOW
        fd=os.open(wf,wf_flags,0o600)
        with os.fdopen(fd,'a',encoding='utf-8') as f:
            f.write(canonical({'schema':'SOL_SESSION_WAVE/1.0','seq':obj['sequence'],'channel':ch,'event_hash':obj['hash'],'data':projections[ch]})+'\n')
            f.flush();os.fsync(f.fileno())
    return verify(root)

def resume(root):
    data=verify(root)
    ev=data['last_event'] or {}
    return {'last_verified_cursor':data['last_hash'],'event_count':data['entries'],
            'objective':ev.get('objective'),'last_action':ev.get('action'),
            'provider_receipt':ev.get('provider_receipt'),'readback':ev.get('readback'),
            'state':ev.get('state'),'next_agent':ev.get('next_agent'),
            'next_user_if_required':ev.get('next_user_if_required'),
            'note':'Stored checkpoint, not automatic current provider status; fresh-read provider before continuing'}

def self_test():
    with tempfile.TemporaryDirectory() as d:
        assert verify(d)['entries']==0
        e={'event_id':'t1','objective':'prepare skill','event':'started','state':'NEXT_AGENT'}
        assert record(d,e)['entries']==1
        assert resume(d)['next_agent'] is None
        for f in CHANNELS.values(): assert (pathlib.Path(d)/f).exists()
        record(d,{'event_id':'t2','objective':'prepare skill','state':'VERIFIED_DONE','provider_receipt':'github:commit','readback':'sha-verified'})
        assert resume(d)['event_count']==2
        try:record(d,e)
        except ValueError:pass
        else: raise AssertionError('duplicate accepted')
        try:record(d,{'event_id':'t3','objective':'test','notes':'Bearer secretbearer1234'})
        except ValueError:pass
        else: raise AssertionError('secret accepted')
        proj=pathlib.Path(d)/CHANNELS['DELTA']
        good=proj.read_text(encoding='utf-8')
        proj.write_text(good.replace('DELTA','THETA'),encoding='utf-8')
        try:verify(d)
        except ValueError:pass
        else:raise AssertionError('tampered wave accepted')
        proj.write_text(good,encoding='utf-8')
        p=pathlib.Path(d)/'CONTINUITY_EVENTS.jsonl'
        body=p.read_text(encoding='utf-8')
        p.write_text(body.replace('github:commit','FAKE_RECEIPT'),encoding='utf-8')
        try:verify(d)
        except ValueError:pass
        else:raise AssertionError('tampered chain accepted')
    print('PASS: session journal self-test (9 assertions/guards)')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--self-test',action='store_true')
    sub=p.add_subparsers(dest='cmd')
    for name in ('record','verify','resume'):
        s=sub.add_parser(name);s.add_argument('--directory',required=True)
        if name=='record':s.add_argument('--input',required=True)
    args=p.parse_args()
    if args.self_test:return self_test()
    if args.cmd=='record':result=record(args.directory,json.loads(pathlib.Path(args.input).read_text(encoding='utf-8')))
    elif args.cmd=='verify':result=verify(args.directory)
    elif args.cmd=='resume':result=resume(args.directory)
    else:p.error('select record, verify, resume or --self-test')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
