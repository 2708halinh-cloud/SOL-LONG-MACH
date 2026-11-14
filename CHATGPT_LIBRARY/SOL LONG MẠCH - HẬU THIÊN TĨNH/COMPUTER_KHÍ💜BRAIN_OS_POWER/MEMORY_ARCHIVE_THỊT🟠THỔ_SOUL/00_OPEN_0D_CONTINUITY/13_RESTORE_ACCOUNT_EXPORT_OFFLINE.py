#!/usr/bin/env python3
"""Giải nén ChatGPT export offline: không gọi mạng, không chạy dữ liệu, không ghi đè.

Usage:
  python 13_RESTORE_ACCOUNT_EXPORT_OFFLINE.py EXPORT.zip DEST --expected-sha256 SHA256
  python 13_RESTORE_ACCOUNT_EXPORT_OFFLINE.py EXPORT.zip DEST --verify-only
"""
import argparse, csv, hashlib, json, pathlib, stat, sys, zipfile
MAX_TOTAL=4*1024**3
MAX_MEMBERS=50000
CHUNK=1024*1024

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(CHUNK), b''):h.update(b)
    return h.hexdigest()

def run():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive',type=pathlib.Path)
    p.add_argument('destination',type=pathlib.Path)
    p.add_argument('--expected-sha256')
    p.add_argument('--verify-only',action='store_true')
    a=p.parse_args()
    actual=digest(a.archive)
    if a.expected_sha256 and actual!=a.expected_sha256.lower():raise ValueError('ZIP_SHA256_MISMATCH')
    root=a.destination.resolve()
    rows=[]
    with zipfile.ZipFile(a.archive) as z:
        infos=z.infolist()
        if len(infos)>MAX_MEMBERS or sum(i.file_size for i in infos)>MAX_TOTAL:
            raise ValueError('ARCHIVE_BUDGET_EXCEEDED')
        seen=set()
        for i in infos:
            rel=pathlib.PurePosixPath(i.filename)
            if not i.filename or rel.is_absolute() or '..' in rel.parts or '\\' in i.filename or ':' in i.filename or stat.S_ISLNK(i.external_attr>>16) or i.filename in seen:
                raise ValueError('UNSAFE_ARCHIVE_ENTRY')
            seen.add(i.filename)
        for i in infos:
            if i.is_dir():continue
            target=root.joinpath(*pathlib.PurePosixPath(i.filename).parts)
            if not target.resolve().is_relative_to(root):raise ValueError('PATH_ESCAPE')
            if a.verify_only:
                if not target.is_file() or target.stat().st_size!=i.file_size:raise ValueError('MISSING_OR_CHANGED_SIZE')
                sha=digest(target)
            else:
                target.parent.mkdir(parents=True,exist_ok=True)
                h=hashlib.sha256();count=0
                with z.open(i) as src,target.open('xb') as dst:
                    while buf:=src.read(CHUNK):
                        dst.write(buf);h.update(buf);count+=len(buf)
                if count!=i.file_size:raise ValueError('TRUNCATED_EXTRACT')
                sha=h.hexdigest()
            rows.append((i.filename,i.file_size,sha))
    if not a.verify_only:
        with (root/'LOCAL_ARCHIVE_INDEX_SHA256.csv').open('x',encoding='utf-8',newline='') as f:
            w=csv.writer(f);w.writerow(['path','bytes','sha256']);w.writerows(rows)
    print(json.dumps({'result':'VERIFIED' if a.verify_only else 'EXTRACTED',
          'zip_sha256':actual,'count':len(rows),'bytes':sum(r[1] for r in rows)},ensure_ascii=False))

if __name__=='__main__':
    try:run()
    except Exception as e:print('ERROR: '+str(e),file=sys.stderr);sys.exit(2)
