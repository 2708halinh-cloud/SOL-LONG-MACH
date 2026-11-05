#!/usr/bin/env python3
"""Read-only task dependency planner and audited N+1 checkpoint generator.

Usage: python progress_gate.py --input plan.json [--output checkpoint.json]
       python progress_gate.py --self-test
Does not execute external actions; only computes the next candidate task.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any

STATUSES = {"pending", "running", "done", "blocked"}


def decide(plan: dict[str, Any]) -> dict[str, Any]:
    tasks = plan.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("tasks must be a non-empty list")
    byid: dict[str, dict[str, Any]] = {}
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("task must be an object")
        name = task.get("id")
        if not isinstance(name, str) or not name or name in byid:
            raise ValueError("missing or duplicate task ID")
        if task.get("status", "pending") not in STATUSES:
            raise ValueError(f"unsupported status: {name}")
        if task.get("status") == "done" and not task.get("readback"):
            raise ValueError(f"done task lacks readback: {name}")
        byid[name] = task
    for name, task in byid.items():
        deps = task.get("depends_on", [])
        if not isinstance(deps, list) or len(set(deps)) != len(deps):
            raise ValueError(f"invalid dependencies: {name}")
        if any(d not in byid for d in deps):
            raise ValueError(f"unknown dependency: {name}")
    visited, visiting = set(), set()
    def dfs(k: str) -> None:
        if k in visiting:
            raise ValueError("dependency cycle")
        if k in visited:
            return
        visiting.add(k)
        for d in byid[k].get("depends_on", []):
            dfs(d)
        visiting.remove(k)
        visited.add(k)
    for key in byid:
        dfs(key)
    completed = [k for k, v in byid.items() if v.get("status") == "done"]
    unfinished = [v for v in tasks if v.get("status", "pending") != "done"]
    ready = [v for v in unfinished if v.get("status", "pending") in {"pending", "running"}
             and all(d in completed for d in v.get("depends_on", []))]
    ready.sort(key=lambda v: (-int(v.get("priority", 0)), tasks.index(v)))
    next_task = ready[0] if ready else None
    if not unfinished:
        state = "VERIFIED_DONE"
    elif next_task is not None:
        state = "NEXT_AGENT"
    else:
        alternatives = [v for v in unfinished if v.get("status") == "blocked" and v.get("alternative")
                        and all(d in completed for d in v.get("depends_on", []))]
        alternatives.sort(key=lambda v: (-int(v.get("priority", 0)), tasks.index(v)))
        if alternatives:
            candidate = alternatives[0]
            next_task = {**candidate, "tool": candidate["alternative"],
                         "description": "Try authorized alternative: " + str(candidate.get("description", candidate["id"]))}
            state = "NEXT_AGENT_ALTERNATIVE"
        else:
            state = "BLOCKED_WITH_CHECKPOINT"
    return {
        "schema": "SOL-AUTONOMY-PERSISTENCE/1.0",
        "objective": plan.get("objective"),
        "state": state,
        "completed": completed,
        "unfinished": [v["id"] for v in unfinished],
        "next_task": {k: next_task.get(k) for k in ("id", "description", "tool", "priority", "approval_required")}
        if next_task else None,
        "blocked": [{"id": v["id"], "reason": v.get("blocker", "unknown"), "alternative": v.get("alternative")}
                    for v in unfinished if v.get("status") == "blocked"],
        "note": "Planner only; execute with authorized host tool then append real receipt and exact-target readback",
    }


def self_test() -> None:
    def t(k: str, status: str = "pending", deps: list[str] | None = None, **kw) -> dict:
        return {"id": k, "status": status, "depends_on": deps or [], **kw}
    cases = [
        ({"tasks": [t("a")]}, "NEXT_AGENT", "a"),
        ({"tasks": [t("a", "done", readback="hash"), t("b", deps=["a"])]}, "NEXT_AGENT", "b"),
        ({"tasks": [t("a", "done", readback="sha")]}, "VERIFIED_DONE", None),
        ({"tasks": [t("a", "blocked", blocker="device offline")]}, "BLOCKED_WITH_CHECKPOINT", None),
        ({"tasks": [t("a", priority=1), t("b", priority=2)]}, "NEXT_AGENT", "b"),
        ({"tasks": [t("a", "blocked", alternative="fallback_tool")]}, "NEXT_AGENT_ALTERNATIVE", "a"),
    ]
    for i, (case, state, nxt) in enumerate(cases, 1):
        got = decide(case)
        assert got["state"] == state and (got["next_task"] or {}).get("id") == nxt, f"case {i}"
    bad = [
        {"tasks": [t("a"), t("a")]},
        {"tasks": [t("a", deps=["missing"])]},
        {"tasks": [t("a", deps=["b"]), t("b", deps=["a"])]},
        {"tasks": [t("a", "done")]},
        {"tasks": []},
    ]
    for i, case in enumerate(bad, 1):
        try:
            decide(case)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid case {i} unexpectedly passed")
    print(json.dumps({"tests": len(cases) + len(bad), "status": "PASS", "schema": "SOL-AUTONOMY-PERSISTENCE/1.0"}, ensure_ascii=False))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path)
    p.add_argument("--output", type=Path)
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        self_test()
        return
    if a.input is None:
        p.error("--input is required unless --self-test")
    result = decide(json.loads(a.input.read_text(encoding="utf-8")))
    raw = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if a.output:
        a.output.write_text(raw, encoding="utf-8")
    else:
        print(raw, end="")


if __name__ == "__main__":
    main()
