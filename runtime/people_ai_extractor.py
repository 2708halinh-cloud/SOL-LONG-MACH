#!/usr/bin/env python3
"""Evidence-first feature extractor for TESSERACT People AI.

Read-only SQLite/JSONL ingestion. Produces inspectable feature rows and a
normalized matrix; does not train weights, alter source databases, or infer
clinical/psychological traits. Text is kept local by default.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, re, sqlite3, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

TEXT_KEYS = re.compile(r"(text|content|message|prompt|response|answer|body|note|cue|decision|reason|value|style|thought|summary|transcript|utterance)", re.I)
POSITIVE = {"đồng ý","chấp nhận","tốt","đúng","ưu tiên","nên","giữ","bảo vệ","xác minh","hoàn thành","agree","accept","good","correct","prefer","should","keep","protect","verify","complete"}
NEGATIVE = {"không","đừng","sai","cấm","từ chối","nguy cơ","lỗi","thiếu","bịa","xóa","dừng","not","don't","wrong","deny","risk","error","missing","fabricate","delete","stop"}
EVIDENCE = {"nguồn","vật chứng","xác minh","đối chiếu","đọc lại","bằng chứng","source","evidence","verify","readback","provenance"}
ACTION = {"thực hiện","triển khai","sửa","chạy","kiểm thử","đồng bộ","xây dựng","execute","implement","fix","run","test","sync","build"}
GOVERNANCE = {"quy tắc","nguyên tắc","cổng","gate","chính sách","quyền","an toàn","policy","rule","principle","safety","permission"}
HUMOR = {"troll","cà khịa","trêu","hài hước","châm biếm","deadpan","humor","sarcasm","tease"}

def tokens(text: str) -> list[str]:
    return re.findall(r"[^\W_]+(?:['’.-][^\W_]+)*", text.casefold(), re.UNICODE)

def bucket_count(words: set[str], vocab: set[str], normalized_text: str = "") -> int:
    # Match both single tokens and multi-word phrases such as "xác minh".
    return sum(1 for term in vocab if (term in words if " " not in term else term in normalized_text))

def features(text: str) -> dict[str, float]:
    ts=tokens(text); n=len(ts); unique=set(ts)
    normalized_text=" ".join(ts)
    sentences=max(1,len(re.findall(r"[.!?。！？]+",text)))
    return {
        "length_tokens": float(n),
        "lexical_diversity": round(len(unique)/n,6) if n else 0.0,
        "mean_sentence_tokens": round(n/sentences,6),
        "evidence_orientation": float(bucket_count(unique,EVIDENCE,normalized_text)),
        "action_orientation": float(bucket_count(unique,ACTION,normalized_text)),
        "governance_orientation": float(bucket_count(unique,GOVERNANCE,normalized_text)),
        "negative_constraint_orientation": float(bucket_count(unique,NEGATIVE,normalized_text)),
        "positive_preference_orientation": float(bucket_count(unique,POSITIVE,normalized_text)),
        "humor_orientation": float(bucket_count(unique,HUMOR,normalized_text)),
        "question_mark_rate": round(text.count("?")/max(1,len(text)),6),
        "imperative_signal": float(bool(re.search(r"\b(hãy|phải|cần|đừng|thực hiện|kiểm tra|must|shall|do not|verify|execute)\b",text,re.I))),
        "first_person_rate": round(sum(1 for w in ts if w in {"tôi","mình","em","anh","i","me","my"})/max(1,n),6),
    }

def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8","replace")).hexdigest()

def iter_sqlite(path: Path, max_rows: int):
    uri=path.resolve().as_uri()+"?mode=ro"
    con=sqlite3.connect(uri,uri=True)
    con.row_factory=sqlite3.Row
    try:
        tables=[r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
        count=0
        for table in tables:
            cols=[r[1] for r in con.execute(f'PRAGMA table_info("{table.replace(chr(34), chr(34)*2)}")')]
            textcols=[c for c in cols if TEXT_KEYS.search(c)]
            if not textcols: continue
            colsql=",".join('"'+c.replace('"','""')+'"' for c in textcols)
            tq='"'+table.replace('"','""')+'"'
            try: rows=con.execute(f"SELECT {colsql} FROM {tq} LIMIT ?",(max_rows,))
            except sqlite3.Error: continue
            for rownum,row in enumerate(rows):
                pieces=[]
                for col in textcols:
                    val=row[col]
                    if isinstance(val,str) and val.strip(): pieces.append((col,val.strip()))
                if not pieces: continue
                text=" | ".join(f"{k}: {v}" for k,v in pieces)
                yield {"source_file":str(path),"source_type":"sqlite","table":table,"row":rownum,"text":text,"sha256":hash_text(text)}
                count+=1
                if count>=max_rows: return
    finally: con.close()

def iter_jsonl(path: Path, max_rows: int):
    with path.open("r",encoding="utf-8-sig",errors="replace") as f:
        for i,line in enumerate(f):
            if i>=max_rows: break
            line=line.strip()
            if not line: continue
            try: obj=json.loads(line)
            except json.JSONDecodeError: continue
            if isinstance(obj,dict):
                parts=[(str(k),v) for k,v in obj.items() if TEXT_KEYS.search(str(k)) and isinstance(v,(str,int,float)) and str(v).strip()]
                if not parts: continue
                text=" | ".join(f"{k}: {v}" for k,v in parts)
                yield {"source_file":str(path),"source_type":"jsonl","table":"","row":i,"text":text,"sha256":hash_text(text)}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source",action="append",default=[],help="SQLite or JSONL path; may be repeated")
    ap.add_argument("--output",default=r"G:\OS_Workspace\TESSERACT_OS\06_Parallel_V\people_ai_extraction")
    ap.add_argument("--max-rows-per-source",type=int,default=50000)
    ap.add_argument("--include-text",action="store_true",help="Include extracted text in JSONL; default stores hash and metadata only")
    args=ap.parse_args()
    out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
    sources=[Path(p) for p in args.source]
    if not sources:
        root=Path(__file__).resolve().parents[1]
        candidates=[root/"03_Synapse_Z"/"synapses_6d.sqlite3",root/"03_Synapse_Z"/"tesseract_er_relations.sqlite3"]
        candidates += sorted((root/"runtime"/"state").glob("*.jsonl"))
        candidates += sorted((root/"continuity").glob("*.jsonl"))
        sources=[p for p in candidates if p.is_file()]
    records=[]; skipped=[]
    for src in sources:
        if not src.is_file():
            skipped.append({"source":str(src),"reason":"NOT_FOUND"}); continue
        try:
            if src.suffix.casefold() in {".sqlite",".sqlite3",".db"}:
                it=iter_sqlite(src,args.max_rows_per_source)
            elif src.suffix.casefold()==".jsonl":
                it=iter_jsonl(src,args.max_rows_per_source)
            else:
                skipped.append({"source":str(src),"reason":"UNSUPPORTED_FORMAT"}); continue
            for rec in it:
                rec.update(features(rec["text"]))
                if args.include_text: rec["text_content"]=rec["text"]
                del rec["text"]
                records.append(rec)
        except (OSError,sqlite3.Error,ValueError) as e:
            skipped.append({"source":str(src),"reason":type(e).__name__,"detail":str(e)[:300]})
    numeric=[k for k in (records[0].keys() if records else []) if k in {"length_tokens","lexical_diversity","mean_sentence_tokens","evidence_orientation","action_orientation","governance_orientation","negative_constraint_orientation","positive_preference_orientation","humor_orientation","question_mark_rate","imperative_signal","first_person_rate"}]
    # Standardized matrix; constant columns map to 0 rather than divide by zero.
    means={k:sum(float(r[k]) for r in records)/len(records) for k in numeric} if records else {}
    stds={k:math.sqrt(sum((float(r[k])-means[k])**2 for r in records)/len(records)) for k in numeric} if records else {}
    matrix=out/"feature_matrix.jsonl"
    with matrix.open("w",encoding="utf-8",newline="\n") as f:
        for r in records:
            row={k:r[k] for k in ("source_file","source_type","table","row","sha256")}
            row.update({k:r[k] for k in numeric})
            row["z_features"]={k:round((float(r[k])-means[k])/stds[k],6) if stds[k] else 0.0 for k in numeric}
            f.write(json.dumps(row,ensure_ascii=False,separators=(",",":"))+"\n")
    raw=out/"extraction_records.jsonl"
    with raw.open("w",encoding="utf-8",newline="\n") as f:
        for r in records: f.write(json.dumps(r,ensure_ascii=False,separators=(",",":"))+"\n")
    summary={"schema":"TESSERACT_PEOPLE_AI_FEATURES/1.0","created_at":datetime.now(timezone.utc).isoformat(),"records":len(records),"sources_requested":len(sources),"sources_skipped":skipped,"feature_names":numeric,"means":means,"stddevs":stds,"outputs":{"matrix":str(matrix),"records":str(raw)},"privacy":{"source_databases_opened_read_only":True,"raw_text_in_outputs":bool(args.include_text),"model_training_performed":False,"psychological_truth_claimed":False}}
    (out/"extraction_receipt.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return 0 if records else 2
if __name__=="__main__": raise SystemExit(main())
