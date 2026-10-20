#!/usr/bin/env python3
"""SOL 10-lane archive classifier. Never extracts or executes archive contents.
No third-party credential consumption. All source archives stay read-only.
"""
from __future__ import annotations
import argparse, bz2, concurrent.futures, gzip, hashlib, json, lzma, os
import re, shutil, subprocess, sys, tarfile, tempfile, time, zipfile
from pathlib import Path, PurePosixPath

MAX_MEMBERS=25000
MAX_EXPANDED=512*1024*1024
MAX_RATIO=300
FORMATS=("ALL","7Z","BZ2","GZ","JAR","LR","RAR","TAR","XZ","ZIP")
HEADERS=((b"7z\xbc\xaf\x27\x1c","7Z"),(b"Rar!\x1a\x07","RAR"),
 (b"LRZI","LR"),(b"\x1f\x8b","GZ"),(b"BZh","BZ2"),
 (b"\xfd7zXZ\x00","XZ"),(b"PK\x03\x04","ZIP"),(b"PK\x05\x06","ZIP"))

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def fmt(path):
    name=path.name.lower()
    with open(path,"rb") as f:head=f.read(512)
    kind=next((v for sig,v in HEADERS if head.startswith(sig)),None)
    if kind=="ZIP" and name.endswith(".jar"):return "JAR"
    if kind=="GZ" and name.endswith((".tar.gz",".tgz")):return "TAR"
    if kind=="BZ2" and name.endswith(".tar.bz2"):return "TAR"
    if kind=="XZ" and name.endswith((".tar.xz",".txz")):return "TAR"
    if len(head)>262 and head[257:262]==b"ustar":return "TAR"
    return kind or "UNRECOGNIZED"

def safe_member(name,symlink=False):
    clean=name.replace("\\","/")
    parts=PurePosixPath(clean).parts
    return not (symlink or clean.startswith("/") or re.match(r"^[A-Za-z]:",clean)
                or ".." in parts or "\x00" in clean)

def stamp(name):
    matches=re.findall(r"(?<!\d)(?:20\d{2}[-_]?[01]\d[-_]?[0-3]\d)(?!\d)",name)
    return matches[:3]

def inspect(path):
    path=Path(path)
    out={"schema":"SOL_ARCHIVE_10_FORMATS_V1","basename":path.name,
      "bytes":path.stat().st_size,"sha256":sha(path),"detected":fmt(path),
      "stamp_old_candidates":stamp(path.name),"account":"ACCOUNT_UNVERIFIED",
      "sensitive_data_copied":False,"extraction_performed":False,
      "adapter":None,"status":"UNSUPPORTED","member_count":None,
      "expanded_bytes":None,"error_code":None}
    kind=out["detected"]
    try:
        if kind in ("ZIP","JAR"):
            out["adapter"]="python.zipfile"
            with zipfile.ZipFile(path) as arc:
                infos=arc.infolist()
                if len(infos)>MAX_MEMBERS:raise ValueError("TOO_MANY_MEMBERS")
                total=sum(x.file_size for x in infos)
                if total>MAX_EXPANDED:raise ValueError("TOO_MUCH_EXPANDED_DATA")
                for f in infos:
                    mode=(f.external_attr>>16)&0o170000
                    if not safe_member(f.filename,mode==0o120000):
                        raise ValueError("UNSAFE_PATH_OR_SYMLINK")
                    if f.file_size>MAX_RATIO*max(f.compress_size,1) and f.file_size>1024*1024:
                        raise ValueError("COMPRESSION_RATIO_TOO_LARGE")
                out["member_count"]=len(infos);out["expanded_bytes"]=total
                names=[z.filename.lower() for z in infos]
                if "conversations.json" in names or "chat.html" in names:
                    out["account"]="OPENAI_CHAT_EXPORT_STRUCTURE_CANDIDATE"
                elif any("codex" in n or n.startswith(".codex/") for n in names):
                    out["account"]="CODEX_STRUCTURE_CANDIDATE"
                if any(x.flag_bits&1 for x in infos):
                    out["status"]="ENCRYPTED"
                elif arc.testzip() is None:
                    out["status"]="PASS"
                else:
                    out["status"]="CRC_FAILED"
        elif kind=="TAR":
            out["adapter"]="python.tarfile"
            with tarfile.open(path,"r:*") as arc:
                total=0;count=0
                for member in arc:
                    count+=1;total+=member.size
                    if count>MAX_MEMBERS or total>MAX_EXPANDED:
                        raise ValueError("ARCHIVE_LIMIT_EXCEEDED")
                    if not safe_member(member.name,member.issym() or member.islnk() or
                                       member.isdev() or member.isfifo()):
                        raise ValueError("UNSAFE_PATH_OR_LINK")
                    if member.isfile():
                        f=arc.extractfile(member)
                        if f is None:raise ValueError("MISSING_TAR_MEMBER")
                        while f.read(1024*1024):pass
                out.update(member_count=count,expanded_bytes=total,status="PASS")
        elif kind in ("GZ","BZ2","XZ"):
            library={"GZ":gzip,"BZ2":bz2,"XZ":lzma}[kind]
            out["adapter"]="python."+library.__name__
            total=0
            with library.open(path,"rb") as f:
                while True:
                    piece=f.read(1024*1024)
                    if not piece:break
                    total+=len(piece)
                    if total>MAX_EXPANDED:raise ValueError("EXPANDED_STREAM_LIMIT")
            out.update(member_count=1,expanded_bytes=total,status="PASS")
        elif kind in ("7Z","RAR","LR"):
            binary=(shutil.which("7z") or shutil.which("7zz")) if kind in ("7Z","RAR") else shutil.which("lrzip")
            if not binary:
                out["status"]="NEEDS_ADAPTER"
            else:
                out["adapter"]=Path(binary).name
                argv=[binary,"t","-bd",str(path)] if kind in ("7Z","RAR") else [binary,"-t",str(path)]
                result=subprocess.run(argv,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                                      timeout=45,stdin=subprocess.DEVNULL)
                out["status"]="PASS" if result.returncode==0 else "TEST_FAILED_OR_ENCRYPTED"
        else:
            out["error_code"]="MAGIC_NOT_RECOGNIZED"
    except (OSError,ValueError,zipfile.BadZipFile,tarfile.TarError,EOFError,
            lzma.LZMAError,bz2.BZ2Decompressor.__class__,subprocess.TimeoutExpired) as e:
        out["status"]="FAILED_SAFE"
        out["error_code"]=type(e).__name__
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("files",nargs="*")
    p.add_argument("--capabilities",action="store_true")
    p.add_argument("--fixture-test",action="store_true")
    p.add_argument("--output")
    a=p.parse_args()
    if a.capabilities:
        print(json.dumps({"formats":list(FORMATS),
          "ALL":"virtual_index","7Z":bool(shutil.which("7z") or shutil.which("7zz")),
          "RAR":bool(shutil.which("7z") or shutil.which("7zz")),
          "LR":bool(shutil.which("lrzip"))}));return
    if a.fixture_test:
        with tempfile.TemporaryDirectory() as dir:
            d=Path(dir);contents=b"safe example"
            with zipfile.ZipFile(d/"test.zip","w") as z:z.writestr("folder/data.txt",contents)
            with zipfile.ZipFile(d/"test.jar","w") as z:z.writestr("META-INF/MANIFEST.MF",contents)
            with tarfile.open(d/"test.tar","w") as t:
                import io
                info=tarfile.TarInfo("folder/a.txt");info.size=len(contents)
                t.addfile(info,io.BytesIO(contents))
            for name,mod in (("test.gz",gzip),("test.bz2",bz2),("test.xz",lzma)):
                with mod.open(d/name,"wb") as f:f.write(contents)
            tests=[inspect(q) for q in sorted(d.iterdir())]
            assert len(tests)==6 and all(x["status"]=="PASS" for x in tests),tests
            print(json.dumps({"fixtures":len(tests),"passed":6,"formats":[x["detected"] for x in tests]}))
        return
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(inspect,a.files))
    if a.output:
        target=Path(a.output)
        if target.exists():raise SystemExit("Refuse to overwrite existing evidence")
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps({"schema":"SOL_ARCHIVE_ALL_INDEX_V1",
            "results":results},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        saved=json.loads(target.read_text("utf-8"))
        if saved["results"]!=results:raise SystemExit("READBACK_FAILED")
    print(json.dumps({"results":results},ensure_ascii=False))
if __name__=="__main__":
    main()
