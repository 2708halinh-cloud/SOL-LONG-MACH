#!/usr/bin/env python3
"""Read-only, stdlib ROM metadata and checksum. Does not execute firmware."""
import argparse,hashlib,json
from pathlib import Path

def inspect(path):
    path=Path(path)
    size=path.stat().st_size
    if size>64*1024*1024: raise ValueError('Image exceeds 64 MiB inspection limit')
    data=path.read_bytes()
    n=len(data)
    out={'file':str(path),'bytes':n,'sha256':hashlib.sha256(data).hexdigest(),
         'full_image_sum_mod_256':sum(data)%256,'full_image_zero_checksum':sum(data)%256==0,
         'is_8k_core_size':n==8192,
         'repeats_8k_block':n in (16384,32768,65536) and data==data[:8192]*(n//8192)}
    if n>=3 and data[:2]==bytes.fromhex('55aa'):
        declared=data[2]*512
        out['extension_rom']={'signature':'55aa','declared_bytes':declared,
            'declared_size_valid':0<declared<=n,
            'declared_sum_mod_256':sum(data[:declared])%256 if 0<declared<=n else None}
    else: out['extension_rom']={'signature':'absent'}
    out['limitations']='Checksum does not prove correct execution, licensing, motherboard compatibility or flash safety.'
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('images',nargs='+',type=Path)
    a=p.parse_args()
    reports=[]
    for file in a.images:
        try: reports.append(inspect(file))
        except (OSError,ValueError) as e:reports.append({'file':str(file),'error':str(e)})
    print(json.dumps(reports,indent=2,ensure_ascii=False))
    return int(any('error' in r for r in reports))
if __name__=='__main__':raise SystemExit(main())
