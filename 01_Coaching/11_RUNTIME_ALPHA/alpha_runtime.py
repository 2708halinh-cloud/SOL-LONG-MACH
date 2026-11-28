#!/usr/bin/env python3
"""ALPHA: read-only identifier/provenance inspection for JSON and SQLite carriers."""
from __future__ import annotations
import argparse, hashlib, json, sqlite3
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import quote

ID_KEYS={"session_id","sessionid","conversation_id","conversationid","project_id","projectid","project_uuid","template_id","templateid"}
ACTOR_KEYS={"actor","subject","author","source_actor","participant","model"}
LAYER_MAP={"hà linh":"01_USER_VERBATIM","ha linh":"01_USER_VERBATIM","user":"01_USER_VERBATIM","mei":"02_MEI_SELF_DESCRIPTION_ACTION","sol":"03_OTHER_SUBJECT","minh":"03_OTHER_SUBJECT","om":"03_OTHER_SUBJECT","xiang":"03_OTHER_SUBJECT","tool":"04_TOOL_READBACK","readback":"04_TOOL_READBACK"}
def sha256_file(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()
def classify_actor(value):
    if not isinstance(value,str) or not value.strip(): return "UNKNOWN","PARTIAL"
    s=value.casefold()
    for label,layer in LAYER_MAP.items():
        if label in s: return layer,"CLASSIFIED_EXPLICIT"
    return "UNKNOWN","PARTIAL"
def collect_ids(obj,out):
    if isinstance(obj,dict):
        for key,val in obj.items():
            k=str(key).casefold().replace("-","_"); compact=k.replace("_","")
            if k in ID_KEYS or compact in {x.replace("_","") for x in ID_KEYS}:
                if isinstance(val,(str,int)) and str(val).strip(): out.setdefault(k,set()).add(str(val))
            collect_ids(val,out)
    elif isinstance(obj,list):
        for v in obj: collect_ids(v,out)
def json_metadata(path):
    doc=json.loads(path.read_text(encoding="utf-8-sig")); ids={}
    collect_ids(doc,ids); actors=[]
    def walk(o):
        if isinstance(o,dict):
            for k,v in o.items():
                if str(k).casefold() in ACTOR_KEYS and isinstance(v,str):
                    layer,status=classify_actor(v); actors.append({"label":v,"layer":layer,"status":status})
                walk(v)
        elif isinstance(o,list):
            for v in o: walk(v)
    walk(doc)
    return {"format":"JSON","identifiers":{k:sorted(v) for k,v in sorted(ids.items())},"explicit_actor_labels":actors}
def sqlite_metadata(path):
    uri="file:"+quote(str(path.resolve()),safe="/:")+"?mode=ro"
    con=sqlite3.connect(uri,uri=True,timeout=2); con.execute("PRAGMA query_only=ON"); tables=[]
    try:
        names=[r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        for name in names:
            qname='"'+name.replace('"','""')+'"'
            cols=[r[1] for r in con.execute("PRAGMA table_info("+qname+")")]
            chosen=[c for c in cols if c.casefold().replace("-","_") in ID_KEYS or c.casefold().replace("-","_").replace("_","") in {x.replace("_","") for x in ID_KEYS}]
            found={}
            if chosen:
                qcols=",".join('"'+c.replace('"','""')+'"' for c in chosen)
                for row in con.execute("SELECT DISTINCT "+qcols+" FROM "+qname+" LIMIT 1000"):
                    for c,v in zip(chosen,row):
                        if v is not None and str(v).strip(): found.setdefault(c.casefold(),set()).add(str(v))
            tables.append({"table":name,"columns":cols,"identifier_columns":chosen,"identifiers":{k:sorted(v) for k,v in sorted(found.items())}})
    finally: con.close()
    return {"format":"SQLITE","read_mode":"READ_ONLY","tables":tables}
def inspect_carrier(path_text,expected_sha256=None):
    p=Path(path_text).expanduser().resolve()
    if not p.exists(): return {"source_path":path_text,"status":"NOT_FOUND","read_coverage":"NONE"}
    before=sha256_file(p)
    if expected_sha256 and before.casefold()!=expected_sha256.casefold():
        return {"source_path":str(p),"status":"HASH_MISMATCH","expected_sha256":expected_sha256,"observed_sha256":before,"read_coverage":"NONE"}
    try:
        if p.suffix.casefold()==".json": meta=json_metadata(p)
        elif p.suffix.casefold() in {".sqlite",".db"}: meta=sqlite_metadata(p)
        else: meta={"format":"OTHER"}
    except Exception as e: meta={"parse_error":type(e).__name__,"format":"UNKNOWN"}
    after=sha256_file(p)
    return {"source_path":str(p),"sha256_before":before,"sha256_after":after,"source_unchanged":before==after,"status":"READBACK_VERIFIED" if before==after else "SOURCE_CHANGED_DURING_READ","read_coverage":"METADATA_ONLY","metadata":meta}
def record_tool_readback(tool_name,source_ref,observed_at,status,output_sha256=None):
    if not all(x.strip() for x in (tool_name,source_ref,observed_at,status)): raise ValueError("required readback fields missing")
    return {"layer":"04_TOOL_READBACK","tool":tool_name,"source_ref":source_ref,"observed_at":observed_at,"status":status,"output_sha256":output_sha256}
def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("carriers",nargs="+"); ap.add_argument("--output",required=True); args=ap.parse_args()
    rows=[inspect_carrier(p) for p in args.carriers]
    doc={"runtime":"ALPHA","created_at_utc":datetime.now(timezone.utc).isoformat(),"operation":"READ_ONLY_IDENTIFIER_PROVENANCE","carrier_count":len(rows),"carriers":rows,"preservation":{"raw_modified":False,"raw_payload_copied":False}}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); tmp=out.with_suffix(out.suffix+".tmp")
    tmp.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); tmp.replace(out)
    print(json.dumps({"output":str(out),"carrier_count":len(rows),"statuses":[x["status"] for x in rows]},ensure_ascii=False))
if __name__=="__main__": main()
