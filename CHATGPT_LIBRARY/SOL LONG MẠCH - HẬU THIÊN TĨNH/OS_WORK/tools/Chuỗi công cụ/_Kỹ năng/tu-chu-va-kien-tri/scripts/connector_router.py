#!/usr/bin/env python3
"""Source-bound MCP connector router: offline, no network or connector invocations.

Consumes a *current-session* tool inventory; never treats app:// as permission.
"""
from __future__ import annotations
import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

APP_MARKDOWN = re.compile(r"\[\$([^]\n]{1,120})\]\(app://([^\s)]+)\)")
NAME_RE = re.compile(r"^mcp__([A-Za-z0-9_]+)__(.+)$")


def norm(s: str) -> str:
    s = unicodedata.normalize('NFD', str(s).casefold())
    return ''.join(x for x in s if unicodedata.category(x) != 'Mn' and x.isalnum())


def explicit_apps(signal: str) -> list[dict[str, Any]]:
    result=[]
    for m in APP_MARKDOWN.finditer(signal):
        ident=m.group(2)
        placeholder='{{' in ident or '}}' in ident or ident.lower() in ('connector_id','id')
        result.append({'display_name':m.group(1),'app_uri_literal':'app://'+ident,
                       'connector_id':None if placeholder else ident,
                       'id_is_placeholder':placeholder,
                       'host_identity_verified':False})
    return result


def providers_from_tools(inventory: dict[str, Any]) -> dict[str,list[str]]:
    out: dict[str,list[str]]={}
    for entry in inventory.get('tools',[]):
        name=entry if isinstance(entry,str) else (entry.get('name') if isinstance(entry,dict) else None)
        if not isinstance(name,str):continue
        m=NAME_RE.fullmatch(name)
        if m:out.setdefault(m.group(1),[]).append(name)
    return out


def route(signal: str, inventory: dict[str,Any], provider_hint: str | None=None) -> dict[str,Any]:
    apps=explicit_apps(signal)
    providers=providers_from_tools(inventory)
    desired=[x['display_name'] for x in apps]
    if provider_hint and not desired:desired=[provider_hint]
    # No fuzzy provider inference from unrelated user words.
    matches=[]
    for d in desired:
        choices=[p for p in providers if norm(p)==norm(d)]
        if not choices:
            choices=[p for p in providers if norm(p).startswith(norm(d)) or norm(d).startswith(norm(p))]
        matches.append({'requested_name':d,'matching_tool_families':choices,
                        'tool_candidates':[name for p in choices for name in providers[p]],
                        'tool_schema_not_yet_checked':bool(choices)})
    if not desired:
        status='NO_APP_ROUTE_REQUESTED_OR_INFERRED'
    elif all(m['matching_tool_families'] for m in matches):
        status='PROVIDER_TOOL_FAMILY_CANDIDATE'
    else:status='DISCOVER_TOOL_OR_CONNECTION'
    return {'status':status,'explicit_refs':apps,'routes':matches,
            'available_tool_names_count':sum(map(len,providers.values())),
            'tool_search_exposed':bool(inventory.get('tool_search_exposed')),
            'resource_listing_exposed':bool(inventory.get('resource_listing_exposed')),
            'discovery_next':('USE_HOST_TOOL_SEARCH_IF_EXPOSED' if inventory.get('tool_search_exposed') else
                              'CHECK_VISIBLE_TOOLS_THEN_AUTHORIZED_PLUGIN_DIRECTORY') if status=='DISCOVER_TOOL_OR_CONNECTION' else None,
            'external_action_executed':False,'permission_granted_by_app_ref':False,
            'provider_identity_verified':False,'source_kind':'CURRENT_SESSION_TOOL_INVENTORY_ONLY'}


def self_test() -> None:
    inv={'tools':['mcp__GitHub__fetch_file','mcp__GitHub__create_file','mcp__Google_Drive__search','mcp__Gmail__search_emails']}
    tests=[
      ('explicit',len(route('Sử dụng [$GitHub](app://abc123)',inv)['explicit_refs'])==1),
      ('id',route('[$GitHub](app://abc123)',inv)['explicit_refs'][0]['connector_id']=='abc123'),
      ('placeholder',route('[$GitHub](app://{{connector_id}})',inv)['explicit_refs'][0]['id_is_placeholder']),
      ('candidate',route('[$GitHub](app://abc123)',inv)['status']=='PROVIDER_TOOL_FAMILY_CANDIDATE'),
      ('no-identity-claim',not route('[$GitHub](app://abc123)',inv)['provider_identity_verified']),
      ('no-permission',not route('[$GitHub](app://abc123)',inv)['permission_granted_by_app_ref']),
      ('implicit',route('task',inv,'Gmail')['routes'][0]['matching_tool_families']==['Gmail']),
      ('none',route('task',inv)['status']=='NO_APP_ROUTE_REQUESTED_OR_INFERRED'),
      ('unknown',route('[$Google Cloud](app://a)',inv)['status']=='DISCOVER_TOOL_OR_CONNECTION'),
      ('search-exposed',route('[$Unknown](app://a)',{**inv,'tool_search_exposed':True})['discovery_next']=='USE_HOST_TOOL_SEARCH_IF_EXPOSED'),
      ('no-network',not route('[$GitHub](app://x)',inv)['external_action_executed']),
      ('not-listed',route('[$Dropbox](app://x)',inv)['status']=='DISCOVER_TOOL_OR_CONNECTION'),
      ('two',len(route('[$GitHub](app://x) + [$Gmail](app://y)',inv)['routes'])==2),
      ('no-id-implicit',route('work',inv,'GitHub')['explicit_refs']==[]),
    ]
    failing=[name for name,ok in tests if not ok]
    print(json.dumps({'tests':len(tests),'passed':len(tests)-len(failing),'failed':failing}))
    if failing:raise AssertionError(failing)


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument('--self-test',action='store_true')
    p.add_argument('--inventory',type=Path)
    p.add_argument('--signal',default='')
    p.add_argument('--provider-hint')
    a=p.parse_args()
    if a.self_test:self_test();return 0
    if not a.inventory:p.error('--inventory required')
    inv=json.loads(a.inventory.read_text(encoding='utf8'))
    print(json.dumps(route(a.signal,inv,a.provider_hint),ensure_ascii=False,indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
