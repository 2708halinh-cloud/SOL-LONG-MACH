#!/usr/bin/env python3
"""SOL POWER router: source-bound group discovery and explicit _Plugins return.

This does not install, connect, activate or execute external plugins.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

ROOT_REL = "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools"
CONFIG = "_Plugins/POWER_ROUTER_CURRENT.json"
BACK = "_Plugins/_Skills/_Mcps/_Tool/_App/_Other_Tools/RETURN_TO_PLUGINS.json"


def _normalize(value: str) -> str:
    text = str(value).casefold().replace("đ", "d")
    return "".join(c for c in unicodedata.normalize("NFD", text)
                   if unicodedata.category(c) != "Mn")


def _safe(tools: Path, relative: str) -> Path:
    candidate = (tools / relative).resolve()
    if not candidate.is_relative_to(tools.resolve()):
        raise ValueError("ROUTE_ESCAPES_TOOLS_ROOT")
    return candidate


def load(repo_root: Path) -> tuple[Path, dict, dict]:
    tools = _safe(repo_root.resolve(), ROOT_REL)
    index = json.loads(_safe(tools, CONFIG).read_text(encoding="utf-8"))
    back = json.loads(_safe(tools, BACK).read_text(encoding="utf-8"))
    if index.get("schema") != "SOL_POWER_ROUTER/1.0":
        raise ValueError("POWER_ROUTER_SCHEMA_MISMATCH")
    if index.get("entrypoint") != "_Plugins":
        raise ValueError("ORIGIN_NOT_PLUGINS")
    if index.get("terminal_back_edge") != BACK:
        raise ValueError("BACK_EDGE_MISMATCH")
    if back.get("target", {}).get("name") != "_Plugins" or back.get("link_type") != "METADATA_POINTER_ONLY":
        raise ValueError("BACK_EDGE_NOT_SOURCE_POINTER")
    source = _safe(tools, str(Path(BACK).parent))
    dest = (source / back["origin_relative_path"]).resolve()
    if dest != _safe(tools, "_Plugins"):
        raise ValueError("RETURN_PATH_MISWIRED")
    groups = index.get("groups", [])
    if len({g["id"] for g in groups}) != len(groups):
        raise ValueError("DUPLICATE_GROUP_ID")
    if len({g["at"] for g in groups if g["id"] != "discovery"}) != len(groups)-1:
        raise ValueError("DUPLICATE_GROUP_PORTAL")
    for group in groups:
        if not _safe(tools, group["at"]).is_dir():
            raise ValueError("GROUP_PORTAL_MISSING:" + group["id"])
        for ref in group.get("sources", []):
            _safe(tools, ref)
    return tools, index, back


def route(task: str, repo_root: Path) -> dict:
    if not task.strip():
        raise ValueError("TASK_REQUIRED")
    tools, index, back = load(repo_root)
    query = _normalize(task)
    scored = []
    for group in index["groups"]:
        matched = [word for word in group["match"] if re.search(
            r"(?<!\\w)" + re.escape(_normalize(word)) + r"(?!\\w)", query)]
        if matched:
            scored.append((len(matched), group["id"], group, matched))
    scored.sort(key=lambda row: (-row[0], row[1]))
    chosen = scored[0][2] if scored else next(g for g in index["groups"] if g["id"] == "discovery")
    observations = []
    for path in chosen["sources"]:
        f = _safe(tools, path)
        observations.append({"relative_path": path,
                             "found_in_checkout": f.exists(),
                             "kind": "directory" if f.is_dir() else "file" if f.is_file() else "missing"})
    # This is a logical traversal. Never follow a filesystem symlink or recurse in an actual cycle.
    visited = []
    for node in index["group_order"]:
        if node in visited:
            raise ValueError("CYCLIC_GROUP_ORDER")
        visited.append(node)
    visited.append("_Plugins_RETURN")
    return {
        "task": task, "selected_group": chosen["id"], "portal": chosen["at"],
        "source_observations": observations,
        "source_route_complete": all(x["found_in_checkout"] for x in observations),
        "return_edge": index["terminal_back_edge"],
        "return_to": back["target"]["name"],
        "return_relation_type": back["link_type"],
        "logical_traversal": visited,
        "next_authorized_probe": chosen["next"],
        "action_executed": False, "live_provider_confirmed": None,
        "readback_scope": "LOCAL_REPOSITORY_CHECKOUT_ONLY",
    }


def main() -> int:
    cli = argparse.ArgumentParser()
    cli.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[6])
    cli.add_argument("--task")
    cli.add_argument("--check", action="store_true")
    args = cli.parse_args()
    if args.check:
        tools, idx, back = load(args.repo_root)
        sample = route("trình duyệt", args.repo_root)
        out = {"passed": True, "groups": len(idx["groups"]),
               "return_to": back["target"]["name"],
               "example_group": sample["selected_group"],
               "scope": "SOURCE_ONLY"}
    else:
        if args.task is None:
            cli.error("--task is required unless --check is used")
        out = route(args.task, args.repo_root)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
