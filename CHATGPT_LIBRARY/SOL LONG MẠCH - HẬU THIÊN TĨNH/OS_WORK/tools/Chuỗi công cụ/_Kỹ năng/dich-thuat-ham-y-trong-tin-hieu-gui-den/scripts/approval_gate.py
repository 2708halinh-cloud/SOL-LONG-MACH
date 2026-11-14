#!/usr/bin/env python3
"""Read-only, auditable task/authorization classification; not an authorization provider.

Usage: python approval_gate.py --input event.json [--output decision.json]
       python approval_gate.py --self-test
All inputs are evidence supplied by the caller. A classification cannot override host permission.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any

EXPLICIT = {"explicit_current", "explicit_prior_scope"}
SCOPE = EXPLICIT | {"implied_task"}
SENSITIVE = {"deploy", "publish", "merge", "irreversible_change", "delete_resource", "third_party_message"}


def classify(event: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(event, dict) or not str(event.get("objective", "")).strip():
        raise ValueError("objective non-empty required")
    action = str(event.get("action", "other"))
    auth = str(event.get("authorization_source", "none"))
    observation = str(event.get("tool_state", "unknown"))
    impact = str(event.get("impact", "unknown"))
    reason = ""
    # The classifier is a cautionary planner. It never issues authorization.
    if event.get("policy_prohibited", False):
        decision, reason = "POLICY_BLOCKED", "Action prohibited by controlling policy"
    elif event.get("automated_review_denied", False):
        decision, reason = "AUTOMATED_REVIEW_DENIED", str(event.get("denial_reason") or "Host refused this operation")
    elif not event.get("source_scope_verified", False):
        decision, reason = "DISCOVER_OR_REPAIR", "Need source, target identity, or action scope verification"
    elif observation not in {"callable", "not_needed"}:
        decision, reason = "DISCOVER_OR_REPAIR", "Callable host tool and actual provider scope not verified"
    elif (action == "third_party_message" or event.get("is_third_party_message", False)) and auth not in EXPLICIT:
        decision, reason = "ASK_AT_FINAL_BOUNDARY", "Messages to others require explicit scoped authorization"
    elif event.get("host_requires_approval", False):
        if event.get("preparation_complete", False):
            decision, reason = "ASK_AT_FINAL_BOUNDARY", "Host or external provider explicitly requires approval"
        else:
            decision, reason = "PREPARE_THEN_APPROVAL", "Prepare reviewable artifacts and tests before the host approval step"
    elif action in SENSITIVE or impact in {"irreversible", "high"}:
        if auth not in EXPLICIT:
            decision = "ASK_AT_FINAL_BOUNDARY" if event.get("preparation_complete", False) else "PREPARE_THEN_APPROVAL"
            reason = "Sensitive or irreversible effect requires explicit scoped authorization"
        else:
            decision, reason = "EXECUTE_NOW", "Explicit authorization recorded; host action may still enforce approval"
    elif auth in SCOPE:
        decision, reason = "EXECUTE_NOW", "Authorization in task scope; no host gate asserted"
    elif action in {"read", "inspect", "review", "test_local", "draft_local"}:
        decision, reason = "EXECUTE_NOW", "Read-only or local preparatory action; no external state change"
    else:
        decision, reason = "DISCOVER_OR_REPAIR", "Authorization evidence for changing external state is missing"
    return {
        "schema": "SOL-INTENT-PERMISSION/1.0",
        "objective": event["objective"],
        "action": action,
        "decision": decision,
        "reason": reason,
        "scope_evidence": auth,
        "host_tool_state": observation,
        "rule": "Decision support only: actual host/provider permissions always apply",
    }


def self_test() -> None:
    base = {"objective": "Read sources", "action": "read", "tool_state": "callable", "source_scope_verified": True}
    cases = [
        ({}, "EXECUTE_NOW"),
        ({"action": "third_party_message"}, "ASK_AT_FINAL_BOUNDARY"),
        ({"action": "third_party_message", "authorization_source": "explicit_prior_scope"}, "EXECUTE_NOW"),
        ({"action": "deploy", "authorization_source": "implied_task"}, "PREPARE_THEN_APPROVAL"),
        ({"action": "deploy", "authorization_source": "implied_task", "preparation_complete": True}, "ASK_AT_FINAL_BOUNDARY"),
        ({"action": "deploy", "authorization_source": "explicit_current"}, "EXECUTE_NOW"),
        ({"action": "read", "host_requires_approval": True}, "PREPARE_THEN_APPROVAL"),
        ({"action": "read", "host_requires_approval": True, "preparation_complete": True}, "ASK_AT_FINAL_BOUNDARY"),
        ({"action": "read", "tool_state": "missing"}, "DISCOVER_OR_REPAIR"),
        ({"action": "read", "source_scope_verified": False}, "DISCOVER_OR_REPAIR"),
        ({"policy_prohibited": True}, "POLICY_BLOCKED"),
        ({"automated_review_denied": True, "denial_reason": "blocked"}, "AUTOMATED_REVIEW_DENIED"),
        ({"action": "write_external"}, "DISCOVER_OR_REPAIR"),
        ({"action": "write_external", "authorization_source": "implied_task"}, "EXECUTE_NOW"),
    ]
    for i, (delta, expected) in enumerate(cases, 1):
        case = {**base, **delta}
        got = classify(case)["decision"]
        assert got == expected, f"case {i}: got {got}, want {expected}"
    print(json.dumps({"tests": len(cases), "status": "PASS", "schema": "SOL-INTENT-PERMISSION/1.0"}, ensure_ascii=False))


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
    result = classify(json.loads(a.input.read_text(encoding="utf-8")))
    out = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if a.output:
        a.output.write_text(out, encoding="utf-8")
    else:
        print(out, end="")


if __name__ == "__main__":
    main()
