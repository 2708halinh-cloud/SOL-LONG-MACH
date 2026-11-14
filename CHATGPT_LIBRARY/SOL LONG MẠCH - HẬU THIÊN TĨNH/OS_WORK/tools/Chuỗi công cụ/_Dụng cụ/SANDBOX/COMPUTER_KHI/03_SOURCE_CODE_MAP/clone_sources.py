#!/usr/bin/env python3
"""Clone public source code to a user-selected persistent path; never overwrite or execute cloned code."""
from __future__ import annotations
import argparse,json,subprocess,shutil
from pathlib import Path

REPOS={
 'registry_editor_open':'https://github.com/reactos/reactos.git',
 'powertoys':'https://github.com/microsoft/PowerToys.git',
 'task_manager_open':'https://github.com/winsiderss/systeminformer.git',
 'remote_desktop_open':'https://github.com/FreeRDP/FreeRDP.git',
 'advanced_rgb':'https://github.com/colour-science/colour.git',
}
SPARSE={
 'registry_editor_open':['base/applications/regedit','sdk/include','base/CMakeLists.txt'],
 'powertoys':['src/modules/colorPicker','src/modules/registrypreview','src/settings-ui','doc/devdocs'],
 'task_manager_open':['SystemInformer','phlib','phnt','plugins','README.md'],
 'remote_desktop_open':['client/Windows','client/SDL','libfreerdp','winpr','README.md'],
 'advanced_rgb':['colour','README.rst','pyproject.toml'],
}

def run(*args):return subprocess.run(args,check=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.strip()

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);p.add_argument('--only',choices=sorted(REPOS));p.add_argument('--full',action='store_true');a=p.parse_args()
    if not shutil.which('git'):p.error('git is not installed')
    if not a.root.is_dir():p.error('Existing persistent destination root is required')
    results=[]
    for name,url in REPOS.items():
        if a.only and name!=a.only:continue
        folder=a.root/name
        if folder.exists():
            results.append({'name':name,'status':'SKIPPED_DESTINATION_EXISTS','folder':str(folder)});continue
        command=['git','clone','--depth=1','--filter=blob:none']
        if not a.full:command+=['--sparse']
        command += [url,str(folder)]
        try:
            run(*command)
            if not a.full:run('git','-C',str(folder),'sparse-checkout','set',*SPARSE[name])
            sha=run('git','-C',str(folder),'rev-parse','HEAD')
            dirty=run('git','-C',str(folder),'status','--porcelain')
            results.append({'name':name,'status':'CLONED','source_url':url,'head_commit':sha,'dirty':bool(dirty),'path':str(folder)})
        except subprocess.CalledProcessError as e:
            results.append({'name':name,'status':'ERROR','reason':(e.stderr or '')[-500:], 'path':str(folder)})
    print(json.dumps({'results':results},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
