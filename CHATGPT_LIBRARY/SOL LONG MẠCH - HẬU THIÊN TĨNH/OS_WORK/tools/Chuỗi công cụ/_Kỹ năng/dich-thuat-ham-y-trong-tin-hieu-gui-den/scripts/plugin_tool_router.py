#!/usr/bin/env python3
"""Source-first plugin/component capability selection. No network, auth or external actions."""
from __future__ import annotations
import argparse
import json
import re
import unicodedata
from pathlib import Path

MCP = re.compile(r'^mcp__([A-Za-z0-9_]+)__(\w+)$')


def normalize(value):
    t=unicodedata.normalize('NFD',str(value).casefold()).replace('đ','d')
    return ''.join(c for c in t if c.isalnum())


def component_inventory(raw):
    """Explicitly supplied host inventory only; no creation of phantom connected tools."""
    tools=[]
    for entry in raw.get('tools',[]):
        if isinstance(entry,str): entry={'name':entry}
        if not isinstance(entry,dict): continue
        name=entry.get('name','')
        match=MCP.fullmatch(name)
        if not match: continue
        tools.append({'name':name,'server':match.group(1),'method':match.group(2),
                      'plugin_origin':entry.get('plugin_origin'),
                      'capabilities':entry.get('capabilities',[]),
                      'callable_observed':entry.get('callable_observed') is True,
                      'schema_checked':entry.get('schema_checked') is True})
    return tools


def route(task, inventory, *, named_plugin=None, needed_capability=None, login_challenge_observed=False):
    """Deterministic preflight; returns candidates and next action, not a permission grant."""
    tools=component_inventory(inventory)
    hint=normalize(named_plugin or '')
    capability=normalize(needed_capability or '')
    candidate=[]
    for tool in tools:
        origin=normalize(tool.get('plugin_origin') or '')
        server=normalize(tool['server'])
        name=normalize(tool['name'])
        caps=[normalize(c) for c in tool['capabilities']]
        # Plugin-name match is an origin hint. Capability is the decisive filter.
        match_plugin=bool(hint) and (hint==origin or hint==server)
        match_cap=bool(capability) and (capability in caps or capability in name)
        if match_cap or (match_plugin and not capability):
            candidate.append({**tool,'matching_plugin_origin':match_plugin,'capability_matched':match_cap})
    # Explicit name without evidence cannot convert a source-only plugin into installed provider.
    candidate.sort(key=lambda x:(not x['capability_matched'],not x['callable_observed'],not x['schema_checked'],x['name']))
    login_needed=bool(login_challenge_observed)
    if login_needed:
        next_edge='READ_MASTER_OATH_THEN_USE_AUTHORIZED_BROWSER_OR_PROVIDER_AUTH_TOOL'
    elif candidate and candidate[0]['callable_observed'] and candidate[0]['schema_checked']:
        next_edge='CALL_SELECTED_MCP_WITH_SCOPED_INPUT_AND_READBACK'
    elif candidate:
        next_edge='CHECK_SELECTED_MCP_SCHEMA_AUTH_AND_CONNECTIVITY'
    else:
        next_edge='DISCOVER_CAPABILITY_IN_CURRENT_TOOLS_AND_SKILL_PROVENANCE'
    return {
      'schema':'SOL_PLUGIN_COMPONENT_ROUTE/1.0','task':task,
      'named_plugin_hint':named_plugin,'needed_capability':needed_capability,
      'observed_tools':len(tools),'candidate_tools':candidate,
      'next_edge':next_edge,'master_oath_applicable':login_needed,
      'administrator_tools_status':'SOURCE_GUIDE_ONLY_UNLESS_EXECUTOR_CONFIRMED',
      'plugin_direct_call_performed':False,'external_action_performed':False,
      'identity_or_permission_inferred_from_name':False,
      'auth_evidence':None,'readback':None,'reentry_required_if_blocked':not bool(candidate)
    }


def self_test():
    test={'tools':[
        {'name':'mcp__GitHub__fetch_file','plugin_origin':'github','capabilities':['repo-read'], 'callable_observed':True,'schema_checked':True},
        {'name':'mcp__GitHub__update_file','plugin_origin':'github','capabilities':['repo-write'], 'callable_observed':True,'schema_checked':True},
        {'name':'mcp__Gmail__send_email','plugin_origin':'gmail','capabilities':['send-mail'],'callable_observed':True,'schema_checked':True},
        {'name':'mcp__Foo__search','plugin_origin':'plugin-master-flatform','capabilities':['skill-author'],'callable_observed':False,'schema_checked':False},
        'mcp__Dropbox__list_files',
        {'name':'fake_tool','plugin_origin':'github','capabilities':['repo-read'],'callable_observed':True,'schema_checked':True}
    ]}
    r=lambda **kw:route('Skill work',test,**kw)
    tests={
        'no-phantoms':len(component_inventory(test))==5,
        'method-unchanged':component_inventory(test)[0]['name']=='mcp__GitHub__fetch_file',
        'plugin-provenance':component_inventory(test)[3]['plugin_origin']=='plugin-master-flatform',
        'name-not-permission':not r(named_plugin='github')['identity_or_permission_inferred_from_name'],
        'plugin-not-direct-called':not r(named_plugin='github')['plugin_direct_call_performed'],
        'route-capability':r(needed_capability='repo-write')['candidate_tools'][0]['name']=='mcp__GitHub__update_file',
        'route-by-origin':r(named_plugin='github')['candidate_tools'][0]['name'].startswith('mcp__GitHub__'),
        'only-doc':r(named_plugin='plugin-master-flatform')['next_edge']=='CHECK_SELECTED_MCP_SCHEMA_AUTH_AND_CONNECTIVITY',
        'unknown':'DISCOVER_CAPABILITY' in r(named_plugin='unknown')['next_edge'],
        'no-login-by-mention':not r(named_plugin='Master OAth')['master_oath_applicable'],
        'login-only-when-observed':r(login_challenge_observed=True)['master_oath_applicable'],
        'auth-route':'MASTER_OATH' in r(login_challenge_observed=True)['next_edge'],
        'no-admin-elevation':r(named_plugin='github')['administrator_tools_status'].startswith('SOURCE_GUIDE_ONLY'),
        'no-private-action':not r(needed_capability='send-mail')['external_action_performed'],
        'independent-mcp':len(r(needed_capability='repo-read')['candidate_tools'])==1,
        'source-not-current':r(named_plugin='unknown')['auth_evidence'] is None,
        'no-credential-field':all('secret' not in t for t in r(named_plugin='github')['candidate_tools']),
    }
    fails=[k for k,v in tests.items() if not v]
    report={'tests':len(tests),'passed':len(tests)-len(fails),'failed':fails}
    print(json.dumps(report,ensure_ascii=False))
    if fails:raise AssertionError(fails)


def main():
    p=argparse.ArgumentParser(description='SOL plugin component preflight, offline')
    p.add_argument('--self-test',action='store_true')
    p.add_argument('--inventory',type=Path)
    p.add_argument('--task',default='')
    p.add_argument('--named-plugin')
    p.add_argument('--capability')
    p.add_argument('--login-challenge-observed',action='store_true')
    args=p.parse_args()
    if args.self_test:self_test();return
    if not args.inventory:p.error('--inventory required')
    inventory=json.loads(args.inventory.read_text(encoding='utf8'))
    print(json.dumps(route(args.task,inventory,named_plugin=args.named_plugin,
       needed_capability=args.capability,login_challenge_observed=args.login_challenge_observed),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
