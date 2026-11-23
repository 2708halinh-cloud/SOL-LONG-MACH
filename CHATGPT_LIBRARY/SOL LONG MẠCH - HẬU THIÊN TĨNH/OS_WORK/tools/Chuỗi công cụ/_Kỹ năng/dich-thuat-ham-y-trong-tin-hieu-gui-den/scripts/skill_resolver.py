#!/usr/bin/env python3
"""Offline skill inventory/alias/source resolver: no provider I/O, no privilege escalation.

Input inventory is a current-session, host-verified JSON snapshot, NOT an old index.
Providers must be invoked by the host after this resolver returns the exact handle.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Any


def normalize(value: str) -> str:
    s = str(value).strip().lstrip('$').casefold().replace('_', '-').replace(' ', '-')
    return re.sub(r'-+', '-', s)


def read_local(path: Path) -> dict:
    if not path.is_file() or path.name.lower() != 'skill.md':
        return {"status": "FILE_NOT_FOUND_OR_NOT_SKILL_MD", "path": str(path)}
    # A symlink or path outside a provided authorized root is NOT an auth grant.
    data = path.read_bytes()
    return {"status": "SKILL_SOURCE_READ", "path": str(path),
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "read_method": "authorized_filesystem"}


def resolve_entry(entry: dict[str, Any], aliases: dict[str, str],
                  orchestrator_arg_supported: bool) -> dict:
    location = str(entry.get('location') or entry.get('uri') or '').strip()
    authority = entry.get('authority') or {}
    if isinstance(authority, dict) and authority.get('kind') == 'orchestrator':
        main = entry.get('main_resource')
        if not main:
            return {"status": "MISSING_ORCHESTRATOR_MAIN_RESOURCE", "name": entry.get('name')}
        if orchestrator_arg_supported:
            return {"status": "PROVIDER_READ_REQUIRED", "method": "skills.read",
                    "authority": authority, "package": entry.get('package'),
                    "main_resource": main, "source_verified": False}
        return {"status": "ORCHESTRATOR_AUTHORITY_ARG_UNSUPPORTED",
                "required": "skills.list({authority:{kind:'orchestrator'}})",
                "host_schema_check": True, "source_verified": False}
    if location.startswith('skills://'):
        return {"status": "PROVIDER_READ_REQUIRED", "method": "skills__read",
                "uri": location, "source_verified": False}
    # Explicit non-filesystem provider URI should not be treated as a path.
    if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', location):
        return {"status": "PROVIDER_READ_REQUIRED", "method": "provider_specific_read",
                "uri": location, "source_verified": False}
    token = location.split('/', 1)[0]
    if re.fullmatch(r'r\d+', token):
        if token not in aliases:
            return {"status": "ALIAS_MAP_MISSING", "alias": token, "source_verified": False}
        root = Path(aliases[token])
        rel = location[len(token):].lstrip('/\\')
        target = (root / rel).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError:
            return {"status": "ALIAS_PATH_ESCAPE_REJECTED", "alias": token}
        return read_local(target)
    if location:
        return read_local(Path(location).expanduser().resolve())
    return {"status": "LOCATION_MISSING", "source_verified": False}


def search_known_roots(name: str, roots: list[str]) -> dict | None:
    for root_str in roots:
        root = Path(root_str).expanduser().resolve()
        candidates = [root / name / 'SKILL.md', root / '_Skills' / name / 'SKILL.md',
                      root / 'skills' / name / 'SKILL.md',
                      root / '.agents' / 'skills' / name / 'SKILL.md']
        if root.name == name:
            candidates.insert(0, root / 'SKILL.md')
        for file in candidates:
            if file.is_file():
                result = read_local(file)
                return {**result, "fallback_discovered": True, "source_root": str(root)}
    return None


def route(name: str, inventory: dict, essential: bool = True) -> dict:
    wanted = normalize(name)
    if not wanted:
        raise ValueError('SKILL_NAME_REQUIRED')
    skills = inventory.get('skills', [])
    aliases = inventory.get('path_aliases') or {}
    orchestrator_arg_supported = bool(inventory.get('supports_orchestrator_authority_arg', False))
    if not isinstance(skills, list) or not isinstance(aliases, dict):
        raise ValueError('INVALID_SESSION_INVENTORY')
    exact = [e for e in skills if isinstance(e, dict) and
             (wanted in [normalize(e.get('name','')), normalize(e.get('display_name',''))])]
    checked = []
    for e in exact:
        result = resolve_entry(e, aliases, orchestrator_arg_supported)
        checked.append(result)
        if result.get('status') in ('SKILL_SOURCE_READ', 'PROVIDER_READ_REQUIRED'):
            return {"named_skill": name, "plan_skill_added": True,
                    "resolution": result, "attempts": checked}
    fallback = search_known_roots(wanted, inventory.get('authorized_search_roots', []))
    if fallback:
        return {"named_skill": name, "plan_skill_added": True,
                "resolution": fallback, "attempts": checked}
    if checked and all(c.get('status') in ('ORCHESTRATOR_AUTHORITY_ARG_UNSUPPORTED', 'ALIAS_MAP_MISSING') for c in checked):
        status = 'PROVIDER_SCHEMA_OR_ALIAS_REQUIRED'
    else:
        status = 'ESSENTIAL_SKILL_NOT_FOUND' if essential else 'SKILL_UNAVAILABLE_NON_BLOCKING'
    return {"named_skill": name, "plan_skill_added": True,
            "resolution": {"status": status, "source_verified": False},
            "attempts": checked, "next": "CHECK_OTHER_AUTHORIZED_SOURCE_OR_REVIEW_MISSING_SKILL"}


def self_test() -> None:
    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        skill = root / 'alpha' / 'SKILL.md'
        skill.parent.mkdir()
        skill.write_text('---\nname: alpha\ndescription: test\n---\nbody\n', encoding='utf8')
        checks = [
            ('local-exact', route('alpha', {"skills": [{"name":"alpha", "location":str(skill)}]})['resolution']['status']=='SKILL_SOURCE_READ'),
            ('fallback-from-root', route('$alpha', {"skills":[],"authorized_search_roots":[str(root)]})['resolution']['status']=='SKILL_SOURCE_READ'),
            ('alias', route('alpha', {"skills":[{"name":"alpha","location":"r0/alpha/SKILL.md"}], "path_aliases":{"r0":str(root)}})['resolution']['status']=='SKILL_SOURCE_READ'),
            ('missing-alias', route('alpha', {"skills":[{"name":"alpha","location":"r0/alpha/SKILL.md"}]})['resolution']['status']=='PROVIDER_SCHEMA_OR_ALIAS_REQUIRED'),
            ('skills-uri', route('alpha', {"skills":[{"name":"alpha","location":"skills://plugins/x/alpha/skill.md"}]})['resolution']['method']=='skills__read'),
            ('essential-missing', route('void', {"skills":[]})['resolution']['status']=='ESSENTIAL_SKILL_NOT_FOUND'),
            ('optional-missing', route('void', {"skills":[]},False)['resolution']['status']=='SKILL_UNAVAILABLE_NON_BLOCKING'),
            ('orchestrator-supported', route('alpha', {"skills":[{"name":"alpha","authority":{"kind":"orchestrator"},"package":"p1","main_resource":"m1"}],"supports_orchestrator_authority_arg":True})['resolution']['method']=='skills.read'),
            ('orchestrator-unsupported', route('alpha', {"skills":[{"name":"alpha","authority":{"kind":"orchestrator"},"package":"p1","main_resource":"m1"}]})['resolution']['status']=='PROVIDER_SCHEMA_OR_ALIAS_REQUIRED'),
            ('not-a-skills-file', route('alpha', {"skills":[{"name":"alpha","location":str(root/'missing.md')}]})['resolution']['status']=='ESSENTIAL_SKILL_NOT_FOUND'),
        ]
        failures=[n for n,passed in checks if not passed]
        print(json.dumps({"tests":len(checks),"passed":len(checks)-len(failures),"failed":failures},ensure_ascii=False))
        if failures:
            raise AssertionError(failures)


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--inventory', type=Path)
    ap.add_argument('--name')
    ap.add_argument('--optional', action='store_true')
    args=ap.parse_args()
    if args.self_test:
        self_test();return 0
    if not args.inventory or not args.name:
        ap.error('--inventory and --name required outside --self-test')
    packet=json.loads(args.inventory.read_text(encoding='utf8'))
    print(json.dumps(route(args.name,packet,not args.optional),ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
