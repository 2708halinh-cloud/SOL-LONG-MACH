#!/usr/bin/env python3
"""Run an existing Google Cloud SOL MCP tool for a selected project alias.

Reads two project IDs from the registry. Reads no OAuth client secret, token,
credential file or private .env. All API calls go through existing gcloud MCP,
using the current authorized gcloud account/config on the execution host.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

BASE = Path(__file__).resolve().parents[2]
REGISTRY = BASE / '_Sổ_đăng_ký/GOOGLE_CLOUD_CAPABILITIES_CURRENT.json'
MCP = Path(__file__).with_name('google_cloud_mcp.py')
ALIAS_RE = re.compile(r'^[a-z][a-z0-9_]{2,64}$')
API_TOOLS = frozenset({
 'gcp_status', 'gcp_projects_list', 'gcp_project_describe',
 'gcp_storage_buckets_list', 'gcp_run_services_list',
 'gcp_compute_instances_list','gcp_enabled_apis_list'
})

def bindings(source: Path=REGISTRY) -> dict:
    body=json.loads(source.read_text(encoding='utf-8'))
    route=body['oauth_clients_reported']
    result={}
    for item in route:
        alias=item['account_alias']
        if not ALIAS_RE.fullmatch(alias) or alias in result:
            raise ValueError('INVALID_OR_DUPLICATE_ALIAS')
        if not re.fullmatch(r'[a-z][a-z0-9-]{4,61}[a-z0-9]',item['project_id']):
            raise ValueError('INVALID_PROJECT_ID')
        result[alias]=item
    if len(result)!=2:
        raise ValueError('EXPECTED_TWO_CONFIGURATIONS')
    return result

def call(alias: str, tool: str, source: Path=REGISTRY) -> dict:
    selected=bindings(source)
    if alias not in selected:
        raise ValueError('UNKNOWN_ACCOUNT_ALIAS')
    if tool not in API_TOOLS:
        raise ValueError('UNKNOWN_READ_ONLY_TOOL')
    data=selected[alias]
    env=os.environ.copy()
    # Credential resolution happens inside gcloud via the named, already authenticated config.
    # When no config is bound, status is still useful, but project API calls are refused
    # so that another account's ambient credentials cannot be mistaken for this one.
    config_name=env.get(data['cloudsdk_config_env'],'').strip()
    if tool!='gcp_status' and not config_name:
        return {'alias':alias,'project':data['project_id'],'executed':False,
                'status':'NO_ACCOUNT_SCOPED_GCLOUD_CONFIG_BOUND'}
    env['SOL_GCP_PROJECT_ID']=data['project_id']
    if config_name:
        if not re.fullmatch(r'[A-Za-z0-9._-]{1,128}',config_name):
            raise ValueError('INVALID_GCLOUD_CONFIG_NAME')
        env['CLOUDSDK_ACTIVE_CONFIG_NAME']=config_name
    req={'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':tool,'arguments':{}}}
    response=subprocess.run([sys.executable,str(MCP)],input=json.dumps(req)+'\n',
                            text=True,capture_output=True,timeout=55,shell=False,env=env)
    if response.returncode or not response.stdout.strip():
        return {'alias':alias,'project':data['project_id'],'executed':False,
                'status':'MCP_PROCESS_FAILED'}
    obj=json.loads(response.stdout.splitlines()[0])
    result=obj.get('result',{})
    if result.get('isError'):
        return {'alias':alias,'project':data['project_id'],'executed':False,
                'status':'PROVIDER_OR_MCP_ERROR'}
    return {'alias':alias,'project':data['project_id'],'executed':True,
            'response':json.loads(result['content'][0]['text'])}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--list',action='store_true')
    p.add_argument('--alias')
    p.add_argument('--tool',default='gcp_status',choices=sorted(API_TOOLS))
    a=p.parse_args()
    if a.list:
        print(json.dumps({'project_routes':[{'alias':x,'project':i['project_id']} for x,i in bindings().items()]},ensure_ascii=False))
    else:
        if not a.alias:p.error('--alias is required unless --list is provided')
        print(json.dumps(call(a.alias,a.tool),ensure_ascii=False))
if __name__=='__main__': main()
