#!/usr/bin/env python3
"""SOL Android/Termux ZIP importer. No network. Never overwrites source files.
The only permitted --apply root is Redmi shared storage: /storage/emulated/0/SOL-LONG-MACH.
"""
import argparse,hashlib,json,stat,zipfile
from pathlib import Path,PurePosixPath

HOME=Path("/storage/emulated/0/SOL-LONG-MACH")
SHARED=Path("/storage/emulated/0")
ROUTES={
 "SOL_GGDV_102_FILES_25_FOLDERS_20261013.zip":"04_KNOWLEDGE/SOURCE_ARCHIVES/SOL_GGDV_20261013",
 "X0_X12_DAO_TAC_NHAN_LOCAL_BUNDLE.zip":"OS_WORK/tools/SOURCE_ARCHIVES/X0_X12_DAO_TAC_NHAN",
 "X_RING_LOCAL_RUNTIME.zip":"OS_WORK/tools/SOURCE_ARCHIVES/X_RING_LOCAL_RUNTIME",
 "unleashed-firmware-dev.zip":"OS_WORK/tools/SUB_GHZ_UNLEASHED_PROTOCOLS/UNLEASHED_FIRMWARE_DEV/SOURCE_ARCHIVE",
}
DENY={".ssh.zip","mcp-remote-v1.zip"}
EXPECTED_ARCHIVE_SHA256={
 "SOL_GGDV_102_FILES_25_FOLDERS_20261013.zip":"f46671a8b1eaf0b4d3bc978df6a64225dc1dfc80abe12f92552a7cfd140a3dab",
 "X0_X12_DAO_TAC_NHAN_LOCAL_BUNDLE.zip":"52704b13a88a34d1791c0861fefcb4ab20cb5898ffdf869593332b946fe50062",
 "X_RING_LOCAL_RUNTIME.zip":"6123898b694d83e6de9e497a0094ffb17d8856cb817b1fe31c4e2b8aa9fd289c",
 "unleashed-firmware-dev.zip":"d0c5c75f790695ccc3b3fccb047a72b454d6694683625cc423114581c61be00f",
}
def digest(b):return hashlib.sha256(b).hexdigest()
def check_member(info):
    n=info.filename;p=PurePosixPath(n)
    if not n or n.startswith("/") or "\\" in n or "\0" in n or ":" in p.parts[0] or any(v in ("..","") for v in p.parts):
        raise ValueError("ZIP_PATH_REJECTED: "+repr(n))
    mode=(info.external_attr >> 16)&0xffff
    if stat.S_ISLNK(mode) or stat.S_ISCHR(mode) or stat.S_ISBLK(mode):
        raise ValueError("ZIP_SPECIAL_ENTRY_REJECTED: "+repr(n))
    if info.file_size>80_000_000 or (info.file_size and info.file_size/max(1,info.compress_size)>500):
        raise ValueError("ZIP_SIZE_RATIO_REJECTED: "+repr(n))
def run(src,root,apply):
    if root.absolute()!=HOME:raise ValueError("BLOCK_PLATFORM_HOME: only /storage/emulated/0/SOL-LONG-MACH")
    if apply and not src.absolute().is_relative_to(SHARED):
        raise ValueError("BLOCK_PLATFORM_SOURCE: source ZIPs must be located on Redmi shared storage")
    out={"schema":"SOL_MULTISPACE_ANDROID_IMPORT/1.0","device_root":str(SHARED),"sol_home":str(HOME),"apply":apply,"archives":[],"files":[],"excluded":sorted(DENY)}
    for filename,subtree in ROUTES.items():
        archive=src/filename
        if not archive.is_file():
            out["archives"].append({"name":filename,"status":"SOURCE_NOT_LOCAL_YET"})
            continue
        archive_bytes=archive.read_bytes()
        if digest(archive_bytes)!=EXPECTED_ARCHIVE_SHA256[filename]:
            raise ValueError("SOURCE_ZIP_SHA256_MISMATCH: "+filename)
        with zipfile.ZipFile(archive) as z:
            entries=z.infolist()
            if sum(i.file_size for i in entries)>150_000_000:raise ValueError("ZIP_TOTAL_SIZE_REJECTED: "+filename)
            count=0
            for entry in entries:
                check_member(entry)
                if entry.is_dir():continue
                destination=HOME/subtree/entry.filename
                if not destination.resolve().is_relative_to(HOME.resolve()):raise ValueError("TARGET_ESCAPE_REJECTED")
                b=z.read(entry);h=digest(b);status="WOULD_WRITE"
                if destination.exists():
                    if destination.is_symlink():raise ValueError("TARGET_LINK_REJECTED")
                    if destination.is_file() and digest(destination.read_bytes())==h:status="UNCHANGED_IDENTICAL"
                    else:
                        destination=destination.with_name(destination.name+".SOURCE_"+h[:12])
                        if destination.exists():
                            if destination.is_file() and digest(destination.read_bytes())==h:
                                status="CONFLICT_ALREADY_PRESENT"
                            else:
                                raise ValueError("CONFLICT_NAME_COLLISION: "+str(destination))
                        else:status="CONFLICT_PRESERVE_NEW_FILE"
                if apply and status in ("WOULD_WRITE","CONFLICT_PRESERVE_NEW_FILE"):
                    destination.parent.mkdir(parents=True,exist_ok=True)
                    with destination.open("xb") as f:f.write(b)
                    status="WRITTEN" if status=="WOULD_WRITE" else "CONFLICT_SAVED"
                out["files"].append({"origin":filename,"path":str(destination.relative_to(HOME)),"bytes":len(b),"sha256":h,"status":status});count+=1
            out["archives"].append({"name":filename,"sha256":digest(archive.read_bytes()),"file_count":count,"status":"APPLIED" if apply else "DRY_RUN"})
    return out
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--apply",action="store_true")
    p.add_argument("--receipt",type=Path)
    a=p.parse_args();result=run(a.source_dir,a.root,a.apply)
    if a.receipt:
        if not a.receipt.absolute().is_relative_to(HOME):raise ValueError("BLOCK_PLATFORM_RECEIPT")
        a.receipt.parent.mkdir(parents=True,exist_ok=True)
        a.receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"apply":a.apply,"archives":result["archives"],"files_examined":len(result["files"])},ensure_ascii=False,indent=2))
