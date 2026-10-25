#!/usr/bin/env python3
"""Diagnose Unleashed firmware build/runtime logs and preflight safe FBT/FAP builds."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

RULES = [
    ("missing_submodule", r'(No module named|No such file or directory|fatal:.*submodule|not found).*\b(nanopb|mbedtls|cmsis|stm32wb|freertos|protobuf|microtar|mlib|heatshrink|submodule)\b|submodule.*(empty|not initialized|not found)', "Restore pinned submodules: git submodule update --init --recursive"),
    ("api_mismatch_fap", r'(api mismatch|API version|API compatibility|App.*not compatible|api_symbols\.csv)', "Check firmware API symbols/version and FAP target; rebuild matching firmware + .fap"),
    ("compile_error", r'(error:|fatal error:|scons: \*\*\*|undefined reference to|ld: cannot find)', "Inspect first compiler/linker diagnostic, source line and toolchain; do not flash partial build"),
    ("crash_assert", r'(hardfault|busfault|memmanage|usagefault|furi_(assert|check)|stack overflow|watchdog|panic|crash|assertion failed)', "Collect timestamp, target/firmware build, stack trace/ELF symbol map, reproduce then isolate smallest failing driver"),
    ("rpc_decode", r'(rpc.*decode|ERROR_DECODE|PB_DECODE_DELIMITED|nanopb.*(fail|invalid)|protobuf.*(invalid|error))', "Check varint-delimited PB_Main framing, packet length, protobuf schema/version, then retry nonmutating read"),
    ("storage", r'(storage.*(error|fail)|fatfs|sd card.*fail|FR_DISK_ERR|filesystem.*corrupt|write.*fail)', "Preserve snapshot; check free space, FS return code, mount/storage service and readback; do not format automatically"),
    ("subghz_protocol", r'(sub.?ghz.*(invalid|unknown|error)|protocol.*(unknown|unsupported)|cc1101.*(error|fail))', "Compare decoder implementation and region/frequency limits; perform offline parsing before RF tests"),
    ("ble_usb", r'(usb.*(disconnect|timeout|error)|ble.*(timeout|disconnect|error)|stm32wb.*(error|timeout))', "Check CDC/BLE transport, STM32WB copro stack and UART framing without automatic firmware flash"),
]

def diagnose(text: str):
    results=[]
    for key, pattern, fix in RULES:
        matches=[]
        for n, line in enumerate(text.splitlines(),1):
            if re.search(pattern,line,re.I):
                matches.append({"line":n,"excerpt":line[:280]})
                if len(matches)>=10:break
        if matches:results.append({"category":key,"matches":matches,"next_probe":fix})
    return {"schema":"SOL_UNLEASHED_DIAGNOSIS/1.0", "categories":results,
            "diagnostics_found":sum(len(x['matches']) for x in results), "mutations":False}

def build_preflight(root: Path, target: str, appsrc: str = ""):
    root=root.resolve()
    missing=[]
    if not (root/'fbt').is_file():missing.append('fbt')
    if not (root/'.git').exists():missing.append('.git checkout/gitlinks (archive alone is not a Git clone)')
    try:
        from unleashed_source_index import parse_submodules
        modules=parse_submodules(root)
        missing += [x['path'] for x in modules if not x['content_in_zip']]
    except (FileNotFoundError,ValueError):missing.append('valid .gitmodules')
    if target=='fap_dist' and appsrc:
        p=(root/appsrc).resolve()
        if not p.is_relative_to(root) or not (p/'application.fam').is_file():
            missing.append('valid application source with application.fam')
    if not shutil.which('git'):missing.append('git command')
    if target not in {'fw_dist','fap_dist','updater_package','vscode_dist'}:
        raise ValueError('Target not on safe build allowlist')
    cmd=['./fbt', 'COMPACT=1', 'DEBUG=0', target]
    if appsrc and target=='fap_dist':cmd += ['APPSRC='+appsrc]
    return {"schema":"SOL_UNLEASHED_BUILD_PREFLIGHT/1.0", "target":target,
            "command":cmd,"cwd":str(root),"blockers":missing,"ready":not missing,
            "flash_requested":False,"build_executed":False}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    subs=parser.add_subparsers(dest='cmd',required=True)
    diag=subs.add_parser('diagnose');diag.add_argument('log',type=Path)
    b=subs.add_parser('build');b.add_argument('source_root',type=Path)
    b.add_argument('--target',choices=['fw_dist','fap_dist','updater_package','vscode_dist'],default='fw_dist')
    b.add_argument('--appsrc',default='');b.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    if args.cmd=='diagnose':
        value=diagnose(args.log.read_text(encoding='utf-8',errors='replace'))
    else:
        value=build_preflight(args.source_root,args.target,args.appsrc)
        if args.execute:
            if not value['ready']:
                value['error']='BUILD_BLOCKED_BY_PREFLIGHT';print(json.dumps(value,ensure_ascii=False,indent=2));return 2
            run=subprocess.run(value['command'],cwd=value['cwd'],capture_output=True,text=True,timeout=3600,check=False)
            value.update(build_executed=True,exit_code=run.returncode,
                         stdout_tail=run.stdout[-2000:],stderr_tail=run.stderr[-2000:])
            value['succeeded']=run.returncode==0
    print(json.dumps(value,ensure_ascii=False,indent=2))
    return 0
if __name__=='__main__':sys.exit(main())
