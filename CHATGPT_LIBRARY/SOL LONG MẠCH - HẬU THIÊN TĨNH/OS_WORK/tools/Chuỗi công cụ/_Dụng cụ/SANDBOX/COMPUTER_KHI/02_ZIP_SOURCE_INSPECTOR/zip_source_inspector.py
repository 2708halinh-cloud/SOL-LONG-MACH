#!/usr/bin/env python3
"""SOL SOURCE_DIRECT ZIP inventory. Does not execute archive members or mutate source.
Produces evidence in a new adjacent result directory. Python stdlib only.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, mimetypes, os, re, shutil, stat, sys, tempfile, zipfile
from pathlib import Path, PurePosixPath

MAX_ENTRIES = 2000
MAX_TOTAL_UNCOMPRESSED = 256 * 1024 * 1024
MAX_SINGLE = 100 * 1024 * 1024
MAX_RATIO = 1000
TEXT_EXTS = {'.txt','.md','.json','.jsonl','.csv','.toml','.xml','.yaml','.yml','.ini','.cfg','.reg','.py','.ps1','.cmd','.bat','.html','.htm','.css','.js','.rs','.c','.h','.cpp','.cs','.sh','.log'}
SECRET_PATTERNS = [re.compile(p, re.I) for p in [r'\b(?:password|refresh_token|access_token|api[_-]?key|client_secret|authorization|cookie)\b\s*[:=]\s*\S+',r'\bsk-[A-Za-z0-9_-]{12,}\b',r'\bya29\.[\w.-]+']]

def digest_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def safe_relative(name):
    if not name or '\\' in name or '\x00' in name or name.startswith('/') or re.match(r'^[A-Za-z]:',name): return None
    p=PurePosixPath(name)
    if any(x in ('..','.') for x in name.split('/')) or not p.parts: return None
    return p

def category(name, sample):
    if sample.startswith(b'PK\x03\x04'): return 'zip_nested'
    if sample.startswith(b'\x7fELF'): return 'binary_executable'
    if sample.startswith(b'MZ'): return 'windows_pe_candidate_unexecuted'
    if sample.startswith(b'%PDF'): return 'pdf'
    if sample.startswith(b'\x89PNG'): return 'image_png'
    if sample.startswith(b'\xff\xd8\xff'): return 'image_jpeg'
    if Path(name).suffix.lower() in TEXT_EXTS: return 'text_candidate'
    return 'unknown_binary_or_document'

def creation_meta(src):
    st=src.stat()
    is_birth=hasattr(st,'st_birthtime')
    return {'filesystem_created_at':dt.datetime.fromtimestamp(st.st_birthtime,dt.timezone.utc).isoformat() if is_birth else None,
      'filesystem_modified_at':dt.datetime.fromtimestamp(st.st_mtime,dt.timezone.utc).isoformat(),
      'creation_source':'stat.st_birthtime' if is_birth else 'UNKNOWN_NOT_EQUAL_ZIP_FILENAME'}

def analyze(src, output, max_total, max_count, extract, preview_bytes):
    if not src.is_file(): raise FileNotFoundError(src)
    with src.open('rb') as f: signature=f.read(4)
    report={'source_path':str(src.resolve()),'source_basename':src.name,'source_suffix':src.suffix.lower(),
       'source_magic_first4_hex':signature.hex(), 'is_zip_magic':signature.startswith((b'PK\x03\x04', b'PK\x05\x06',b'PK\x07\x08')),
       'archive_size_bytes':src.stat().st_size,'sha256':digest_file(src),**creation_meta(src),
       'archive_status':'INSPECTED','extracted':False,'extraction_reason':'not attempted','entries':[],
       'limits':{'entry_count':max_count,'uncompressed_total':max_total,'single_file':MAX_SINGLE,'compression_ratio_max':MAX_RATIO}}
    if not zipfile.is_zipfile(src):
        report['archive_status']='NOT_ZIP';return report
    unsafe=[];total=0
    with zipfile.ZipFile(src) as z:
        infos=z.infolist()
        report['zip_file_count']=len(infos)
        if len(infos)>max_count: unsafe.append('entry_count_limit_exceeded')
        names=set(); members=[]
        for inf in infos:
            rel=safe_relative(inf.filename)
            unix_mode=(inf.external_attr>>16)&0xffff
            symlink=stat.S_ISLNK(unix_mode)
            encrypted=bool(inf.flag_bits & 1)
            duplicate=inf.filename.casefold() in names
            names.add(inf.filename.casefold())
            individual_over=inf.file_size>MAX_SINGLE
            total+=inf.file_size
            ratio=(inf.file_size/max(inf.compress_size,1)) if inf.file_size else 0
            reasons=[key for key,cond in [('unsafe_path',rel is None),('symlink',symlink),('encrypted',encrypted),('duplicate_name',duplicate),('single_file_limit',individual_over),('compression_ratio_exceeded',ratio>MAX_RATIO)] if cond]
            if reasons:unsafe.append(f'{inf.filename}:{";".join(reasons)}')
            ent={'name':inf.filename,'size_bytes':inf.file_size,'compressed_size_bytes':inf.compress_size,
             'date_time_in_zip':f'{inf.date_time[0]:04}-{inf.date_time[1]:02}-{inf.date_time[2]:02}T{inf.date_time[3]:02}:{inf.date_time[4]:02}:{inf.date_time[5]:02}',
             'timestamp_warning':'ZIP date-time is metadata, not filesystem creation time', 'crc32_header':f'{inf.CRC:08x}',
             'is_directory':inf.is_dir(),'path_allowed':rel is not None,'reasons':reasons,'category':'directory' if inf.is_dir() else None,
             'sha256_uncompressed':None,'content_preview_redacted':None}
            report['entries'].append(ent);members.append((inf,ent))
        report['uncompressed_total_bytes']=total
        if total>max_total: unsafe.append('total_uncompressed_limit_exceeded')
        disk=shutil.disk_usage(str(output.parent)).free
        report['free_space_target_bytes_at_inspection']=disk
        if total > disk - 100*1024*1024: unsafe.append('insufficient_free_space_with_100MiB_reserve')
        if not unsafe:
            # Run CRC/hash/preview even if extraction was not requested.
            for inf,ent in members:
                if inf.is_dir():continue
                h=hashlib.sha256(); sample=bytearray()
                with z.open(inf) as f:
                    for buf in iter(lambda:f.read(65536),b''):
                        h.update(buf)
                        if len(sample)<preview_bytes:sample.extend(buf[:preview_bytes-len(sample)])
                ent['sha256_uncompressed']=h.hexdigest();ent['category']=category(inf.filename,bytes(sample))
                if ent['category']=='text_candidate':
                    try: snippet=bytes(sample).decode('utf-8')[:preview_bytes]
                    except UnicodeDecodeError: snippet=None
                    if snippet is not None:
                        for p in SECRET_PATTERNS:snippet=p.sub('[REDACTED_CREDENTIAL]',snippet)
                        ent['content_preview_redacted']=snippet
            report['archive_status']='CRC_AND_MEMBER_HASHES_VERIFIED'
        else:
            report['archive_status']='INSPECTION_LIMIT_OR_RISK'
        report['issues']=unsafe
        if extract and not unsafe:
            output.mkdir(parents=True,exist_ok=True)
            folder=output/'EXTRACTED';folder.mkdir(exist_ok=False)
            # All names prechecked; stream once again to destination, no extractall.
            try:
                for inf,ent in members:
                    dest=folder.joinpath(*PurePosixPath(inf.filename).parts)
                    if inf.is_dir():dest.mkdir(parents=True,exist_ok=True);continue
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    with z.open(inf) as f,open(dest,'xb') as target:shutil.copyfileobj(f,target,length=65536)
                    if digest_file(dest)!=ent['sha256_uncompressed']:raise RuntimeError(f'post-extraction SHA mismatch {inf.filename}')
                report['extracted']=True;report['extraction_reason']='all_members_sha256_verified'
            except Exception:
                shutil.rmtree(folder,ignore_errors=True);raise
        elif extract:report['extraction_reason']='blocked_due_to_inventory_limits_or_unsafe_members'
    return report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('source',type=Path)
    ap.add_argument('--output',type=Path,default=None)
    ap.add_argument('--max-total-mib',type=int,default=256)
    ap.add_argument('--max-count',type=int,default=2000)
    ap.add_argument('--preview-bytes',type=int,default=160)
    ap.add_argument('--no-extract',action='store_true')
    a=ap.parse_args();src=a.source.expanduser();max_bytes=a.max_total_mib*1024*1024
    if a.output:out=a.output.expanduser()
    else:out=src.parent/(src.name+'.SOL_INVENTORY_'+digest_file(src)[:12])
    if not out.parent.exists():raise SystemExit('Output parent directory does not exist')
    if out.exists():raise SystemExit(f'Output already exists; refusing overwrite: {out}')
    result=analyze(src,out,max_bytes,a.max_count,not a.no_extract,min(4096,max(0,a.preview_bytes)))
    out.mkdir(parents=True,exist_ok=True)
    (out/'SOURCE_DIRECT_ZIP_REPORT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'report':str(out/'SOURCE_DIRECT_ZIP_REPORT.json'),'status':result['archive_status'],'members':len(result.get('entries',[])),'extracted':result['extracted'],'issues':len(result.get('issues',[]))},ensure_ascii=False))

if __name__=='__main__':main()
