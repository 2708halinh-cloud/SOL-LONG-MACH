#!/usr/bin/env python3
"""SOL Administrator System's × Azure Toolset: executable source preflight and routing.

This does not create Windows/ChatGPT/Azure admin privileges or contact Azure.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path

POLICY = ("CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/"
          "COMPUTER_KHÍ💜BRAIN_OS_POWER/MEMORY_ARCHIVE_THỊT🟠THỔ_SOUL/"
          "KINH THÁNH THE MASTER TEACHER/ĐẠO ĐỨC THE MASTER TEACHER/ETHICS_POLICY_CURRENT.json")
TOOLS = "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/Chuỗi công cụ"
AZURE = TOOLS + "/_MCPs/AZURE_DEVOPS_MCP_CORE"
FAMILIES = AZURE + "/SOL_NINE_CAPABILITY_FAMILIES.json"


def source(root: Path, relative: str) -> Path:
    base = root.resolve()
    path = (base / relative).resolve()
    if not path.is_relative_to(base) or not path.is_file():
        raise ValueError("SOURCE_ABSENT_OR_OUTSIDE_REPOSITORY: " + relative)
    return path


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise ValueError("PYTHON_SOURCE_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def preflight(root: Path) -> dict:
    root = root.resolve()
    policy = json.loads(source(root, POLICY).read_text(encoding="utf-8"))
    if policy.get("schema") != "SOL_MASTER_TEACHER_ETHICS/1.0":
        raise ValueError("POLICY_SCHEMA_INVALID")
    if policy.get("roles", {}).get("DUONG_PHAP_SU", {}).get("designation") != "Administrator System's — SOL PROJECT ONLY":
        raise ValueError("PROJECT_ADMIN_ROLE_MISMATCH")
    if policy.get("scope") != "SOL_PROJECT_GOVERNANCE_NOT_PLATFORM_OR_DEVICE_PRIVILEGE":
        raise ValueError("PROJECT_ADMIN_SCOPE_INVALID")
    toolset_index = json.loads(source(root, AZURE + "/TOOLSET_INDEX.json").read_text(encoding="utf-8"))
    source_md = source(root, AZURE + "/docs/TOOLSET.md").read_text(encoding="utf-8")
    parser = load_module(source(root, AZURE + "/route_toolset.py"), "sol_azure_toolset_parser")
    routes = parser.parse_source(source_md)
    indexed = toolset_index.get("entries", [])
    counts = (len(routes), len({v["tool"] for v in routes}), len({v["category"] for v in routes}))
    if counts != (97, 44, 9) or indexed != routes:
        raise ValueError("AZURE_TOOLSET_INDEX_DIVERGENCE")
    families = json.loads(source(root, FAMILIES).read_text(encoding="utf-8"))
    if families.get("schema") != "SOL_TOOLSET_SEMANTIC_TRANSLATION_V1" or len(families.get("families", [])) != 9 or len({f["id"] for f in families["families"]}) != 9:
        raise ValueError("SEMANTIC_FAMILIES_INVALID")
    return {
        "schema": "SOL_ADMINISTRATOR_TOOLSET_PREFLIGHT/1.0",
        "source_checks_passed": True,
        "project_role": policy["roles"]["DUONG_PHAP_SU"]["designation"],
        "operator_role": policy["roles"]["AM_PHAP_SU"]["designation"],
        "azure_source_routes": counts[0], "azure_source_tools": counts[1],
        "azure_source_categories": counts[2], "semantic_families": len(families["families"]),
        "source_policy": POLICY, "toolset_source": AZURE + "/docs/TOOLSET.md",
        "runtime_executed_this_process": True,
        "remote_azure_action_executed": False,
        "actual_provider_admin_granted": False,
        "chatgpt_system_privileges_changed": False,
        "scope": "SOURCE_BOUND_PROJECT_GOVERNANCE_AND_ROUTING_ONLY",
    }


def select(root: Path, task: str) -> dict:
    evidence = preflight(root)
    semantic = load_module(source(root, "runtime/sol_toolset_semantic_router.py"), "sol_toolset_selector")
    registry = json.loads(source(root, FAMILIES).read_text(encoding="utf-8"))
    ethics = load_module(source(root, "runtime/master_teacher_ethics.py"), "sol_ethics_gate")
    decision = ethics.assess(root, {
        "action_type": "read", "actor_role": "AM_PHAP_SU",
        "source_ref": AZURE + "/docs/TOOLSET.md",
        "target": "SOL project governance/toolset capability",
        "action_executed": False,
    })
    capability = semantic.recommend(task, registry)
    return {**evidence, "task": task, "governance_decision": decision["decision"],
            "capabilities": capability["candidates"],
            "next_callable_edge": capability["next"],
            "return_to": "_Plugins", "toolset_as_live_mcp_inferred": False}


def main() -> int:
    cli = argparse.ArgumentParser(description="Administrator System's project authority × Toolset source preflight")
    cli.add_argument("--repo-root", type=Path, default=Path.cwd())
    cli.add_argument("--task", help="Optional source-bound route selection; does not call Azure")
    args = cli.parse_args()
    try:
        result = select(args.repo_root, args.task) if args.task else preflight(args.repo_root)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"source_checks_passed": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())