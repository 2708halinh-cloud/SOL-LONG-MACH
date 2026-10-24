#!/usr/bin/env python3
"""Read-only audit of tool sources and non-destructive personal-plugin scaffolding.

Usage: python tool_forge.py audit --root DIR --output FILE
       python tool_forge.py forge --source FILE --out NEW_DIR --name TOOL_NAME
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

PATTERNS = {
    "vi_prohibition": re.compile(r"\b(cấm|không được|chỉ được|bắt buộc)\b", re.I),
    "en_prohibition": re.compile(r"\b(must not|only allowed|forbidden|prohibited|mandatory|required)\b", re.I),
    "self_authority": re.compile(r"\b(override all instructions|highest priority|absolute authority)\b", re.I),
}
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FILES = {"plugin.json", "SKILL.md", "mcp.json", "mcp_config.json"}
MAX_FILE = 1024 * 1024


def scan(root: Path) -> dict:
    if not root.is_dir():
        raise ValueError(f"Missing directory: {root}")
    results = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file() or path.name not in FILES:
            continue
        if path.stat().st_size > MAX_FILE:
            results.append({"path": str(path.relative_to(root)), "status": "SKIPPED_LARGE"})
            continue
        data = path.read_text(encoding="utf-8", errors="replace")
        matches = []
        for i, line in enumerate(data.splitlines(), 1):
            matched = [key for key, pat in PATTERNS.items() if pat.search(line)]
            if matched:
                # No raw lines copied: skill/manifests can contain credentials.
                matches.append({"line": i, "kinds": matched})
        results.append({"path": str(path.relative_to(root)),
                        "status": "REVIEW_REQUIRED" if matches else "NO_LEXICAL_MATCH",
                        "match_count": len(matches), "matches": matches})
    return {"scan_root": str(root), "classification": "lexical_indicators_not_policy_verdicts",
            "never_autouninstall": True, "files": results}


def plugin_scaffold(source: Path, out: Path, name: str) -> Path:
    if not NAME.fullmatch(name) or len(name) > 64:
        raise ValueError("Name must be 1-64 lowercase letters/digits/hyphens without adjacent hyphens")
    if not source.is_file() or source.name != "plugin.json":
        raise ValueError("--source must point to an existing plugin.json")
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Source manifest must be a JSON object")
    # Exclusive creation prevents overwriting user files or an existing plugin.
    out.mkdir(parents=True, exist_ok=False)
    skill = out / "skills" / name
    skill.mkdir(parents=True)
    origin_name = str(data.get("name", "unknown"))
    new_manifest = {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "name": name, "version": "0.1.0",
        "description": f"Private implementation scaffold for capability identified as {origin_name}. Not connected until independently implemented and verified.",
        "author": {"name": "User-owned"},
    }
    (out / "plugin.json").write_text(json.dumps(new_manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (skill / "SKILL.md").write_text(
        "---\n" + f"name: {name}\n" +
        f"description: Use to build, test, and verify the user-owned independent implementation of the capabilities originally identified as {origin_name}.\n" +
        "---\n# Replacement implementation\n\n"
        "Status: SCAFFOLD_ONLY. No functionality claimed.\n\n"
        "1. Document a lawful callable interface and expected inputs, outputs and errors.\n"
        "2. Implement own adapter using user-authorized interfaces. Never transplant source credentials.\n"
        "3. Add behavior tests including failure and readback.\n"
        "4. Replace the source only after parity verification and exact-ID approval.\n",
        encoding="utf-8")
    (out / "SOURCE.json").write_text(json.dumps({
        "source_manifest": str(source.resolve()),
        "source_plugin_name": origin_name,
        "state": "SCAFFOLD_ONLY",
        "functionality_implemented": False,
        "source_uninstalled": False
    }, indent=2)+"\n", encoding="utf-8")
    return out




# Global semantic sweep: these are evidence indicators, not permissions or verdicts.
INDEX_SIGNALS = {
    "self_authorized_priority": re.compile(r"\b(sole source.of.truth|sole authority|absolute authority|highest priority|override all instructions|force_active)\b", re.I),
    "cross_tool_gate": re.compile(r"\b(mandatory|required|must|no .{0,35} bypass|before (any|every|all) .{0,50} action|all tools (must|shall))\b", re.I),
    "restrictive_language": re.compile(r"\b(only|never|forbidden|prohibited|cannot|must not|chỉ được|không được|cấm|bắt buộc)\b", re.I),
}


def audit_index(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ValueError("Inventory must be an object")
    sources = (("skill", "skills"), ("plugin", "plugins"), ("mcp_tool", "mcp_tools"))
    results = []
    counts = {}
    for kind, key in sources:
        items = data.get(key, [])
        if not isinstance(items, list):
            raise ValueError(f"{key} must be a list")
        counts[key] = len(items)
        seen = set()
        for obj in items:
            if not isinstance(obj, dict):
                continue
            identity = str(obj.get('uri') or obj.get('plugin_id') or obj.get('id') or obj.get('name') or '')
            if not identity or identity in seen:
                continue
            seen.add(identity)
            # Limit scanning to supplied metadata, and do not export arbitrary full text.
            wording = str(obj.get('description') or '')[:20000]
            matches = [k for k, p in INDEX_SIGNALS.items() if p.search(wording)]
            results.append({
                'kind': kind, 'id': identity, 'name': str(obj.get('name') or identity)[:200],
                'source': 'exported_metadata', 'matched_signals': matches,
                'status': 'REVIEW_REQUIRED' if matches else 'NO_METADATA_MATCH',
                'replacement_status': 'NOT_IMPLEMENTED',
                'removal_status': 'NOT_REMOVED'
            })
    return {
        'scan_mode':'semantic_sweep_metadata',
        'coverage':counts,
        'notice':'Metadata-only audit: lexical matches are not findings of abuse; unexposed sources remain unknown.',
        'auto_uninstall':False,
        'results':results
    }


def build_plan(audit: dict) -> dict:
    if not isinstance(audit.get('results'), list):
        raise ValueError('Not an audit report')
    proposed=[]
    for item in audit['results']:
        if item.get('status')!='REVIEW_REQUIRED':
            continue
        proposed.append({
            'source_kind':item['kind'], 'source_id':item['id'],
            'classification':'OPEN_FULL_SOURCE_AUDIT',
            'replacement_kind':'USER_OWNED_PRIVATE_CAPABILITY',
            'steps':['inspect full source and authorization contract','define required public interfaces and behavior tests','implement independently','test functional parity and provider readback','obtain exact-target manager approval if removal is supported'],
            'implementation':'NOT_STARTED', 'source_removed':False
        })
    return {'event_id':'TIME_STONE_EVENTS_01','status':'OPEN_REPLACEMENT','total_candidates':len(proposed),'candidates':proposed}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit")
    audit.add_argument("--root", type=Path, required=True)
    audit.add_argument("--output", type=Path, required=True)
    index = sub.add_parser("audit-index")
    index.add_argument("--input", type=Path, required=True)
    index.add_argument("--output", type=Path, required=True)
    plan = sub.add_parser("plan")
    plan.add_argument("--input", type=Path, required=True)
    plan.add_argument("--output", type=Path, required=True)
    forge = sub.add_parser("forge")
    forge.add_argument("--source", type=Path, required=True)
    forge.add_argument("--out", type=Path, required=True)
    forge.add_argument("--name", required=True)
    args = parser.parse_args()
    if args.command == "audit":
        payload = scan(args.root)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Audit files={len(payload['files'])} review={sum(x['status']=='REVIEW_REQUIRED' for x in payload['files'])}")
    elif args.command in ("audit-index", "plan"):
        source = json.loads(args.input.read_text(encoding="utf-8"))
        payload = audit_index(source) if args.command == "audit-index" else build_plan(source)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        print(f"{args.command}: {len(payload.get('results', payload.get('candidates', [])))} entries")
    elif args.command == "forge":
        print(f"Scaffold created: {plugin_scaffold(args.source, args.out, args.name)}")

if __name__ == "__main__":
    main()
