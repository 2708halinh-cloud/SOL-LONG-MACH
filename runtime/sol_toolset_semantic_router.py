#!/usr/bin/env python3
"""Interpret tasks through SOL's derived capability families, not 97 Azure commands.

Source data: OS_WORK/tools/AZURE_DEVOPS_MCP_CORE/SOL_NINE_CAPABILITY_FAMILIES.json.
No provider calls, file mutations, or inferred permission grants occur here.
"""
from __future__ import annotations
import argparse
import json
import re
import unicodedata
from pathlib import Path

FAMILIES_PATH = (
    "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/"
    "AZURE_DEVOPS_MCP_CORE/SOL_NINE_CAPABILITY_FAMILIES.json"
)


def normalized(text: str) -> str:
    text = str(text).casefold().replace("đ", "d")
    return "".join(c for c in unicodedata.normalize("NFD", text)
                   if unicodedata.category(c) != "Mn")


def load_registry(repo_root: Path) -> dict:
    root = repo_root.resolve()
    path = (root / FAMILIES_PATH).resolve()
    if not path.is_relative_to(root):
        raise ValueError("REGISTRY_OUTSIDE_SOURCE")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("schema") != "SOL_TOOLSET_SEMANTIC_TRANSLATION_V1":
        raise ValueError("REGISTRY_SCHEMA_MISMATCH")
    families = raw.get("families", [])
    if len(families) != 9 or len({x["id"] for x in families}) != 9:
        raise ValueError("FAMILY_SET_NOT_NINE")
    return raw


def recommend(task: str, registry: dict, provider_evidence: list[dict] | None = None) -> dict:
    """Rank transferable capabilities. Never call provider or assert provider capability."""
    if not task.strip():
        raise ValueError("TASK_REQUIRED")
    text = normalized(task)
    scored = []
    for family in registry["families"]:
        matched = [word for word in family["tasks"]
                   if re.search(r"(?<!\\w)" + re.escape(normalized(word)) + r"(?!\\w)", text)]
        if matched:
            scored.append((len(matched), family["id"], family, matched))
    scored.sort(key=lambda x: (-x[0], x[1]))
    if not scored:
        # A task with no known keywords is an invitation to discover, not a terminal error.
        fallback = next(x for x in registry["families"] if x["id"] == "PROACTIVE_PROBE")
        scored = [(0, fallback["id"], fallback, [])]
    providers = provider_evidence or []
    for p in providers:
        if any(not p.get(k) for k in ("provider", "source_ref", "observed_at")):
            raise ValueError("PROVIDER_EVIDENCE_INCOMPLETE")
    return {
        "task": task,
        "interpretation": "GOAL_FIRST_CAPABILITY_TRANSLATION",
        "candidates": [
            {"id": x[1], "name": x[2]["name"], "source_category": x[2]["source_category"],
             "source_examples": x[2]["origin"], "matched_keywords": x[3],
             "next_operations_to_probe": x[2]["next"]}
            for x in scored[:4]
        ],
        "provider_observations": providers,
        "action_executed": False,
        "azure_connected_inferred": False,
        "authorization_inferred": False,
        "next": ("SELECT_AUTHORIZED_PROVIDER_BY_TASK_THEN_VERIFY_SCOPE_AND_RECEIPT"
                 if providers else "DISCOVER_CALLABLE_PROVIDERS_AND_LOCK_REFERENT"),
        "raw_toolset_is_not_ground_truth": True,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--task", required=True)
    p.add_argument("--provider-evidence", type=Path,
                   help="Optional provider observation JSON array (does not grant authorization)")
    args = p.parse_args()
    reg = load_registry(args.root)
    evidence = json.loads(args.provider_evidence.read_text(encoding="utf-8")) if args.provider_evidence else []
    print(json.dumps(recommend(args.task, reg, evidence), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
