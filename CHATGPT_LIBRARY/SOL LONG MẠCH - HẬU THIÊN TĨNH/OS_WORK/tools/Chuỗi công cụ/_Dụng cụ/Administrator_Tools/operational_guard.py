#!/usr/bin/env python3
"""SOL Administrator Tools: read-only operational guard for STOP/READBACK/NEXT.

Not a Windows driver, privileged filter, browser extension, or interception layer.
Call explicitly before every action in an integrated orchestrator; fail closed
when action metadata is missing. No OS writes are performed by this module.
"""
from __future__ import annotations
import argparse
import json
import re
from typing import Any
from source_bridge import read_events

SCHEMA = "SOL_ADMIN_OPERATIONAL_GUARD/1.0"
DANGEROUS_ACTIONS = frozenset({
    "format", "format_volume", "quick_format", "force_format", "diskpart_clean",
    "delete_partition", "remove_partition", "initialize_disk", "wipe_disk",
    "erase_volume", "overwrite_disk", "delete_source_without_verified_backup",
    "delete_folder", "remove_folder", "remove_directory", "rmdir", "rm_rf", "rd_s_q", "purge_directory", "delete_tree",
})
READ_ACTIONS = frozenset({"inspect", "read", "list", "hash", "verify", "diff", "review", "search", "backup_read"})
ORDINARY_ACTIONS = frozenset({"copy", "move_verified", "write_staging", "append_log", "update_reversible", "fix_bug"})
REPORT_ACTIONS = frozenset({"report", "readback", "final", "announce_complete", "handoff"})

# An explicit name controls decision; words in user conversation alone MUST NOT
# trigger machine operations or authorizations.
def _action(value: Any) -> str:
    if not isinstance(value, str): return "unknown"
    return re.sub(r"[^a-z0-9_]+", "_", value.lower().strip()).strip("_") or "unknown"


def assess(request: dict, *, root=None) -> dict:
    """A policy result, never execution. Always return a concrete AGENT next step."""
    if not isinstance(request, dict): raise TypeError("REQUEST_MUST_BE_OBJECT")
    state = read_events(root) if root is not None else read_events()
    kind = _action(request.get("action"))
    target = str(request.get("target", ""))
    receipts = request.get("receipts") or []
    if not isinstance(receipts, list): raise TypeError("RECEIPTS_MUST_BE_LIST")
    verified = bool(request.get("source_verified")) and bool(request.get("target_verified"))
    is_user_final = bool(request.get("user_decision_only"))
    task_open = not state.get("task_complete", False)
    blockers = []
    action = "ALLOW_PREFLIGHT_ONLY"
    actor = "AGENT"
    next_step = state["next_agent"]

    # Any destructive storage action is STOPPED. No text/agent status can override it.
    if kind in DANGEROUS_ACTIONS:
        action = "BLOCK"
        blockers = ["DESTRUCTIVE_STORAGE_OPERATION", "PROTECT_EXISTING_DATA_AND_RECOVERY_OPTIONS"]
        next_step = "STOP_STORAGE_MUTATION_AND_PRESERVE_DEVICE_STATE"
    elif kind in REPORT_ACTIONS and task_open:
        if kind == "handoff" and is_user_final and request.get("specific_user_action"):
            action = "REQUIRE_REAL_USER_DECISION"
            actor = "USER"
            next_step = request["specific_user_action"]
        else:
            action = "BLOCK_PREMATURE_COMPLETION"
            blockers = ["TASK_OPEN", "REPORT_IS_NOT_EXECUTION", "READBACK_REQUIRES_NEXT_AGENT_ACTION"]
    elif kind in READ_ACTIONS:
        action = "ALLOW_READ_ONLY"
    elif kind in ORDINARY_ACTIONS:
        if not verified and kind in {"move_verified", "update_reversible"}:
            action = "REQUIRE_SOURCE_TARGET_VERIFICATION"
            blockers = ["SOURCE_TARGET_PARITY_NOT_PROVEN"]
            next_step = "VERIFY_SOURCE_HASH_TARGET_AND_RECOVERABLE_BACKUP"
        else:
            action = "ALLOW_PREFLIGHT_ONLY"
    else:
        action = "BLOCK_UNCLASSIFIED_OPERATION"
        blockers = ["UNKNOWN_ACTION_METADATA"]
        next_step = "IDENTIFY_EXACT_OPERATION_AND_SOURCE_BEFORE_ACTION"

    # A chat or local self-test cannot prove an actual external state-changing action.
    provider_receipt_valid = bool(receipts) and all(
        isinstance(x, dict) and x.get("source") in {"provider", "device_readback"}
        and bool(x.get("id")) for x in receipts
    )
    if kind in REPORT_ACTIONS and not provider_receipt_valid:
        blockers.append("EXTERNAL_PROVIDER_RECEIPT_NOT_SUPPLIED")
    return {
        "schema": SCHEMA,
        "decision": action,
        "action": kind,
        "target": target,
        "task_complete": state["task_complete"],
        "readback": "VERIFIED_LOCAL_LEDGER_ONLY",
        "provider_action_executed": False,
        "provider_receipts_claimed": len(receipts),
        "provider_receipts_structurally_valid": provider_receipt_valid,
        "blockers": list(dict.fromkeys(blockers)),
        "next_actor": actor,
        "next_action": next_step,
        "risk_context": {
            "reported_volume": "F:",
            "screenshot_capacity_gb": 19.6,
            "screenshot_free_gb": 19.5,
            "screenshot_in_use_format_warning": True,
            "actual_data_loss_extent": "NOT_ESTABLISHED_BY_SCREENSHOTS_ALONE",
        },
        "integration_required": "CALL_BEFORE_PROVIDER_MUTATION_AND_CHECK_DECISION",
        "note": "This gate does not and cannot intercept Windows Disk Management GUI or ChatGPT tool calls automatically.",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", required=True)
    parser.add_argument("--target", default="")
    parser.add_argument("--source-verified", action="store_true")
    parser.add_argument("--target-verified", action="store_true")
    args = parser.parse_args(argv)
    result=assess(vars(args))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["decision"].startswith("ALLOW") else 2

if __name__ == "__main__":
    raise SystemExit(main())