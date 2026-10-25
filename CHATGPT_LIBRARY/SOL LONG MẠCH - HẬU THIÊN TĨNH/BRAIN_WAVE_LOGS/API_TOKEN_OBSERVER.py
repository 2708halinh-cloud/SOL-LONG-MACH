#!/usr/bin/env python3
"""BRAIN_WAVE_LOGS observer: explicit provider response + dashboard import, no secret/API access."""
import argparse, csv, hashlib, json, os
from pathlib import Path
from datetime import datetime, timezone

FILES=["1_RAW_INPUT_OUTPUT.log","2_SPATIAL_VECTOR.log","3_LOGPROBS_GATING.log","4_TEMP_STATE.log","5_CHRONO_CONTINUOUS.log","6_API_TOKEN_USAGE.log","7_API_DASHBOARD_USAGE.log","8_IOTA_DELTA_EVENT.log"]

def now():
    return datetime.now(timezone.utc).isoformat()

def sha(b):
    return hashlib.sha256(b).hexdigest()

def load(p):
    blob=Path(p).read_bytes()
    if len(blob)>64*1024*1024: raise ValueError("File >64MiB")
    return json.loads(blob),blob

def val(x):
    if isinstance(x,bool): return None
    if isinstance(x,str) and x.strip().isascii() and x.strip().isdigit(): x=int(x.strip())
    return x if isinstance(x,int) and x>=0 else None

def usage(response):
    u=response.get("usage") or (response.get("response") or {}).get("usage") or {}
    if not isinstance(u,dict): u={}
    inp=val(u.get("input_tokens",u.get("prompt_tokens")))
    out=val(u.get("output_tokens",u.get("completion_tokens")))
    tot=val(u.get("total_tokens"))
    ci=u.get("input_tokens_details") or u.get("prompt_tokens_details") or {}
    co=u.get("output_tokens_details") or u.get("completion_tokens_details") or {}
    return {"input_tokens":inp,"output_tokens":out,"total_tokens":tot,
            "cached_tokens":val(ci.get("cached_tokens")),
            "reasoning_tokens":val(co.get("reasoning_tokens")),
            "measurement":"PROVIDER_REPORTED" if any(v is not None for v in (inp,out,tot)) else "UNAVAILABLE"}

def append(root,name,row):
    root.mkdir(parents=True,exist_ok=True)
    with (root/name).open("a",encoding="utf-8") as h:
        h.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n")
        h.flush()
        os.fsync(h.fileno())

def rows(path):
    if not path.exists(): return []
    out=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        try: out.append(json.loads(line))
        except ValueError: pass
    return out

def wave(t,id,layer,category,status,data):
    return {"schema":"SOL_WAVE_EVENT/1.0","observed_at":t,"turn_id":id,
            "layer":layer,"wave":category,"status":status,"data":data}

def ingest(a):
    response,rb=load(a.response)
    if not isinstance(response,dict): raise ValueError("Response must be JSON object")
    request,qb=load(a.request) if a.request else ({},None)
    if not isinstance(request,dict): raise ValueError("Request must be JSON object")
    model=response.get("model") or (response.get("response") or {}).get("model") or request.get("model") or a.model
    response_id=response.get("id") or (response.get("response") or {}).get("id")
    eid="api_"+sha((a.provider+":"+str(model)).encode()+b"\x00"+(qb or b"")+b"\x00"+rb)[:24]
    root=Path(a.log_dir)
    if any(x.get("causal_id")==eid for x in rows(root/FILES[5])):
        print(json.dumps({"status":"DEDUPED","causal_id":eid}));return
    t=now()
    u=usage(response)
    fresh="FRESH_OBSERVED" if u["measurement"]=="PROVIDER_REPORTED" else "UNRESOLVED"
    max_output=val(request.get("max_output_tokens",request.get("max_completion_tokens",request.get("max_tokens"))))
    private=None
    if a.private_root:
        private_root=Path(a.private_root).expanduser().resolve()
        if private_root == root.resolve() or root.resolve() in private_root.parents:
            raise ValueError("--private-root must be OUTSIDE the BRAIN_WAVE_LOGS folder")
        private_root.mkdir(parents=True,exist_ok=True,mode=0o700)
        private=private_root/(eid+".json")
        fd=os.open(private,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,"w",encoding="utf-8") as h:
            json.dump({"request":request if qb is not None else None,"response":response},h,ensure_ascii=False)
    row={"schema":"SOL_TOKEN_OBSERVATION/1.0","causal_id":eid,"observed_at":t,
         "source_kind":"API_RESPONSE_FILE","provider":a.provider,"model_id":model,
         "provider_response_id":response_id,"request_sha256":sha(qb) if qb else None,
         "response_sha256":sha(rb),"request_bytes":len(qb) if qb else None,
         "response_bytes":len(rb),"token_usage":u,"configured_max_output_tokens":max_output,
         "context_window_limit":None,"provider_max_output_limit":None,
         "private_payload_retention":"PRIVATE_LOCAL_ONLY" if private else "NOT_SAVED",
         "private_locator_local_only":str(private) if private else None,
         "freshness_state":fresh,"recheck_trigger":"NEW_PROVIDER_RESPONSE_OR_DEPLOYMENT",
         "state_n":"USAGE_NOT_OBSERVED","state_n_plus_1":u["measurement"]}
    append(root,FILES[5],row)
    for filename,layer,category,fields in [
        (FILES[0],"raw","BETA",{"event":"API_IO_PACKET","request_sha256":row["request_sha256"],"response_sha256":row["response_sha256"],"request_bytes":row["request_bytes"],"response_bytes":row["response_bytes"]}),
        (FILES[1],"spatial","BETA",{"event":"PROVIDER_IDENTITY","provider":a.provider,"model_id":model,"provider_response_id":response_id,"usage_ref":eid}),
        (FILES[2],"logprobs","GAMMA",{"event":"TOKEN_USAGE_GATE","measurement":u["measurement"],"logprobs":"NOT_OBSERVED"}),
        (FILES[3],"temp","THETA",{"event":"REQUEST_CONFIG","max_output_tokens":max_output,"model_hard_limit":None}),
        (FILES[4],"chrono","DELTA",{"event":"USAGE_IMPORTED_FROM_API_RESPONSE","provider_called_by_collector":False,"continuation_cursor":eid,"freshness_state":fresh})]:
        append(root,filename,wave(t,eid,layer,category,"OBSERVED",fields))
    append(root,FILES[7],{"schema":"SOL_IOTA_DELTA_EVENT/1.0","causal_id":eid,"delta_ref":eid,
            "source_id":a.provider,"source_revision_or_time":response_id or t,
            "observed_at":t,"freshness_state":fresh,"recheck_trigger":row["recheck_trigger"],
            "observed_state":{"model_id":model,"usage_measurement":u["measurement"]},
            "provider_receipt":response_id,"consequence":"LOCAL_USAGE_LOG_APPENDED",
            "technical_verification":"LOCAL_JSONL_WRITE","unresolved":["CHATGPT_UI_USAGE","MODEL_HARD_LIMIT"],
            "state_n":"USAGE_NOT_OBSERVED","state_n_plus_1":u["measurement"],
            "input_packet":{"previous_output_ref":None,"source_ref":eid},
            "output_packet":{"input_ref":eid,"delta_ref":eid},"continuation_cursor":eid})
    print(json.dumps({"status":"RECORDED","causal_id":eid,"measurement":u["measurement"]}))

def dashboard(a):
    path=Path(a.source);raw=path.read_bytes()
    if len(raw)>64*1024*1024: raise ValueError("File >64MiB")
    data=list(csv.DictReader(raw.decode("utf-8-sig").splitlines())) if path.suffix.lower()==".csv" else json.loads(raw)
    if isinstance(data,dict): data=data.get("data",[])
    if not isinstance(data,list): raise ValueError("Export must contain list of rows")
    root=Path(a.log_dir)
    existing={x.get("causal_id") for x in rows(root/FILES[6])}
    count=0
    for i,item in enumerate(data):
        if not isinstance(item,dict):continue
        u=usage({"usage":item})
        if u["measurement"]=="UNAVAILABLE":continue
        eid="dashboard_"+sha((a.provider+":"+sha(raw)+":"+str(i)).encode())[:24]
        if eid in existing:continue
        append(root,FILES[6],{"schema":"SOL_TOKEN_OBSERVATION/1.0","source_kind":"DASHBOARD_EXPORT_ROW",
              "causal_id":eid,"provider":a.provider,"observed_at":now(),
              "model_id":item.get("model"),"window_start":item.get("start_time",item.get("date")),
              "window_end":item.get("end_time"),"export_sha256":sha(raw),
              "row_index":i,"token_usage":u,"freshness_state":"HISTORICAL_EXPORT",
              "recheck_trigger":"NEW_EXPORT","model_hard_limit":None})
        count+=1
    print(json.dumps({"status":"IMPORTED","rows_with_usage":count}))

def summary(a):
    totals={}
    for filename in ([FILES[5],FILES[6]] if a.include_dashboard else [FILES[5]]):
        for row in rows(Path(a.log_dir)/filename):
            k=(row.get("source_kind"),row.get("provider"),row.get("model_id"))
            if k not in totals:totals[k]={"records":0,"with_usage":0,"input_tokens":0,"output_tokens":0,"total_tokens":0}
            g=totals[k];g["records"]+=1
            u=row.get("token_usage") or {}
            if u.get("measurement")=="PROVIDER_REPORTED":
                g["with_usage"]+=1
                for key in ("input_tokens","output_tokens","total_tokens"):
                    if val(u.get(key)) is not None:g[key]+=val(u[key])
    print(json.dumps({"schema":"SOL_TOKEN_SUMMARY/1.0",
        "groups":[{"source_kind":k[0],"provider":k[1],"model_id":k[2],**v}
                  for k,v in sorted(totals.items(),key=lambda t:str(t[0]))],
        "note":"Provider usage only, not ChatGPT UI usage; no unknowns treated as zero"},ensure_ascii=False,indent=2))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest="cmd",required=True)
    x=sub.add_parser("ingest")
    x.add_argument("--provider",required=True);x.add_argument("--request")
    x.add_argument("--response",required=True);x.add_argument("--model")
    x.add_argument("--log-dir",default=str(Path(__file__).resolve().parent))
    x.add_argument("--private-root");x.set_defaults(func=ingest)
    x=sub.add_parser("dashboard")
    x.add_argument("--provider",required=True);x.add_argument("--source",required=True)
    x.add_argument("--log-dir",default=str(Path(__file__).resolve().parent))
    x.set_defaults(func=dashboard)
    x=sub.add_parser("summary")
    x.add_argument("--log-dir",default=str(Path(__file__).resolve().parent))
    x.add_argument("--include-dashboard",action="store_true")
    x.set_defaults(func=summary)
    args=p.parse_args()
    args.func(args)
if __name__=="__main__":
    main()
