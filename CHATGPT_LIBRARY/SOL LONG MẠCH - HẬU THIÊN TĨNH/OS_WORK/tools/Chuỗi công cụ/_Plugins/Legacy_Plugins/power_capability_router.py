#!/usr/bin/env python3
"""SOL Power Router v2: match actual capabilities; never impersonate provider execution."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import unicodedata
from pathlib import Path

ROOT_REL = "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools"
REGISTRY = "_Plugins/POWER_CAPABILITY_ROUTES_V2.json"
LEGACY = "_Plugins/power_router.py"


def normalize(s: str) -> str:
    s = unicodedata.normalize("NFD", str(s).casefold().replace("đ", "d"))
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")


def load(repo_root: Path):
    repo = repo_root.resolve()
    tools = (repo / ROOT_REL).resolve()
    if not tools.is_relative_to(repo) or not tools.is_dir():
        raise ValueError("TOOLS_ROOT_MISSING_OR_ESCAPES_REPO")
    source = tools / REGISTRY
    if source.is_symlink():
        raise ValueError("REGISTRY_SYMLINK_REFUSED")
    info = json.loads(source.read_text(encoding="utf-8"))
    if info.get("schema") != "SOL_POWER_CAPABILITY_ROUTER/2.0":
        raise ValueError("REGISTRY_SCHEMA_INVALID")
    spec = importlib.util.spec_from_file_location("sol_original_power_router", tools / LEGACY)
    legacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy)
    _, parent, back = legacy.load(repo)
    if back.get("target", {}).get("name") != "_Plugins":
        raise ValueError("RETURN_EDGE_NOT_PLUGINS")
    if info.get("return_pointer") != parent.get("terminal_back_edge"):
        raise ValueError("REGISTRY_BACK_EDGE_MISMATCH")
    ids = [x["id"] for x in info["capabilities"]]
    if len(ids) != len(set(ids)):
        raise ValueError("DUPLICATE_CAPABILITY_ID")
    return repo, tools, info, legacy


def route(task: str, repo_root: Path) -> dict:
    if not isinstance(task, str) or not task.strip():
        raise ValueError("TASK_REQUIRED")
    repo, tools, info, legacy = load(repo_root)
    normalized = normalize(task)
    choices = []
    for cap in info["capabilities"]:
        hits = [word for word in cap["aliases"] if re.search(
            r"(?<!\w)" + re.escape(normalize(word)) + r"(?!\w)", normalized
        )]
        if not hits:
            continue
        portal = next((g["at"] for g in json.loads(
            (tools / info["prior_router"]).read_text(encoding="utf-8")
        )["groups"] if g["id"] == cap["group"]), None)
        if not portal:
            raise ValueError("UNKNOWN_CATEGORY:" + cap["group"])
        if not (tools / portal).is_dir():
            raise ValueError("CATEGORY_PORTAL_MISSING:" + cap["group"])
        choices.append({
            "capability_id": cap["id"], "matched_aliases": hits,
            "score": max(len(normalize(x)) for x in hits),
            "category_portal": portal, "kind": cap["kind"],
            "source_or_tool_ref": cap["entry"], "next_probe": cap["next"],
            "provider_callable_verified_this_run": False,
        })
    choices.sort(key=lambda x: (-x["score"], x["capability_id"]))
    parent_route = legacy.route(task, repo)
    if not choices:
        next_edge = "DISCOVER_SKILLS_AND_PROVIDER_CAPABILITIES"
    elif choices[0]["kind"] in {"SKILL", "LOCAL_BLUEPRINT", "TOOLSET_BLUEPRINT", "CAPABILITY_BLUEPRINT"}:
        next_edge = choices[0]["next_probe"]
    else:
        next_edge = "CHECK_TOOL_SCHEMA_AUTH_AND_PROVIDER_STATE"
    return {
        "schema": "SOL_POWER_ROUTER_DECISION/2.0",
        "input": task,
        "entrypoint": "_Plugins",
        "candidates": choices,
        "next_action": next_edge,
        "legacy_route": parent_route["selected_group"],
        "return_to": parent_route["return_to"],
        "return_edge": info["return_pointer"],
        "cycle_closed_by_metadata": parent_route["return_to"] == "_Plugins",
        "action_executed": False,
        "provider_receipt": None,
        "readback": None,
        "capability_scope": "PROVENANCE_BOUND_DISCOVERY_ONLY",
        "if_not_callable": "DISCOVER_ALTERNATE_CONNECTED_TOOL_OR_HUMAN_AUTH_STEP",
        "never_terminal_label_only": "OPEN_REQUIRES_NEXT_ACTION",
    }


def main():
    arg = argparse.ArgumentParser()
    arg.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[5])
    arg.add_argument("--task", required=True)
    parsed = arg.parse_args()
    print(json.dumps(route(parsed.task, parsed.repo_root), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
