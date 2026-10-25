#!/usr/bin/env python3
"""Audit gitlink-pinned submodules and safely resume an upstream firmware checkout.

Never guesses submodule commit hashes from a ZIP. Only initializes declared
paths in a verified Git checkout; ordinary preflight is offline/read-only.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys
from unleashed_source_index import parse_submodules

UPSTREAM={'https://github.com/DarkFlippers/unleashed-firmware',
          'https://github.com/DarkFlippers/unleashed-firmware.git'}

def git(root:Path,*argv,timeout:int=20):
    cmd=['git','-C',str(root),*argv]
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout,check=False)
    return {'exit':p.returncode,'stdout':p.stdout[-10000:],'stderr':p.stderr[-1000:]}

def inspect(root:Path)->dict:
    root=root.resolve()
    result={'schema':'SOL_UNLEASHED_SUBMODULE_PREFLIGHT/1.0',
            'root':str(root),'git_checkout':(root/'.git').exists(),
            'submodules':[],'origin_verified':False,'needs_update':[],
            'ready_for_recursive_build':False}
    if not (root/'.gitmodules').is_file():
        result['error']='GITMODULES_MISSING';return result
    declared=parse_submodules(root)
    result['declared_count']=len(declared)
    if not result['git_checkout']:
        result['error']='ARCHIVE_NOT_CHECKOUT';return result
    origin=git(root,'remote','get-url','origin')
    result['origin_verified']=origin['exit']==0 and origin['stdout'].strip().rstrip('/') in UPSTREAM
    status=git(root,'submodule','status','--recursive',timeout=45)
    if status['exit']!=0:
        result['error']='GIT_SUBMODULE_STATUS_FAILED'
        result['git_error']=status['stderr'];return result
    statuses={}
    for row in status['stdout'].splitlines():
        if len(row)<42:continue
        bits=row[1:].split()
        if len(bits)>=2:
            statuses[bits[1]]={'state':{'-':'UNINITIALIZED','+':'COMMIT_MISMATCH','U':'MERGE_CONFLICT',' ':'PINNED_MATCH'}.get(row[0],'UNKNOWN'),
                               'commit':bits[0]}
    for module in declared:
        path=module['path']
        st=statuses.get(path)
        observed={'path':path,'gitlink':st['commit'] if st else None,
                  'state':st['state'] if st else 'MISSING_GITLINK'}
        result['submodules'].append(observed)
        if observed['state']!='PINNED_MATCH':result['needs_update'].append(path)
    result['ready_for_recursive_build']=not result['needs_update'] and result['origin_verified']
    return result

def initialize(root:Path,execute:bool=False)->dict:
    report=inspect(root)
    if not execute:return report
    if not report['git_checkout'] or not report['origin_verified']:
        report['error']='UNVERIFIED_UPSTREAM_CHECKOUT'
        return report
    if not report['needs_update']:
        report['action']='NO_CHANGES_NEEDED';return report
    # Never --force, never reset a modified working tree, never flash firmware.
    cmd=git(root,'submodule','update','--init','--recursive',timeout=1500)
    report['update_exit_code']=cmd['exit']
    report['update_stderr_tail']=cmd['stderr'][-700:]
    report['action']='SUBMODULE_UPDATE_ATTEMPTED'
    report['readback']=inspect(root)
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path)
    p.add_argument('--execute',action='store_true')
    a=p.parse_args()
    try:
        result=initialize(a.root,a.execute)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0 if result.get('ready_for_recursive_build') or result.get('readback',{}).get('ready_for_recursive_build') else 2
    except (OSError,ValueError,subprocess.TimeoutExpired) as e:
        print(json.dumps({'error':str(e)}),file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())
