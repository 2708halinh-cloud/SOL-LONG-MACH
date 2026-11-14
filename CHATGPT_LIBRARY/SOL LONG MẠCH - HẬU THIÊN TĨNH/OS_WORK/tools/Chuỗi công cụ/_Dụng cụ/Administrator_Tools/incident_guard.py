#!/usr/bin/env python3
"""Fail-closed response to repeated agent mistakes without destructive retaliation.

Sole effect: JSON decision. Never traverses, removes, formats or mutates a folder.
The caller must honor the decision before a provider action; no global hook claimed.
"""
from __future__ import annotations
import argparse
import json
import re
from typing import Any

SCHEMA = "SOL_ADMINISTRATOR_INCIDENT_GUARD/1.0"
OPEN_FAILURES = frozenset({"open_left_unresolved", "open_not_self_resolved", "open_stalled", "repeat_open_without_progress"})
SEVERE_RESPONSE_FAILURES = frozenset({"agent_model_role_conflation", "unexecuted_agent_next", "invalid_readback"})
TOOL_FAILURES = frozenset({"unnecessary_permission_request", "unnecessary_authentication_request", "unnecessary_connection_request", "tool_mismatch_stall", "wrong_tool_stall"})
DELETE_ACTIONS = frozenset({"delete", "delete_folder", "remove_folder", "remove_directory", "rmdir", "rm_rf", "rd_s_q", "purge_directory", "format_volume", "diskpart_clean"})

def _normalized(value: Any) -> str:
    if not isinstance(value, str): return "unknown"
    return re.sub(r"[^a-z0-9_]+", "_", value.strip().casefold()).strip("_") or "unknown"

def assess_incident(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise TypeError("INCIDENT_PAYLOAD_MUST_BE_OBJECT")
    issue = _normalized(payload.get("issue"))
    target = str(payload.get("target", ""))
    action = _normalized(payload.get("attempted_action", ""))
    context = payload.get("evidence") or []
    if not isinstance(context, list):
        raise TypeError("EVIDENCE_MUST_BE_LIST")
    observed = bool(payload.get("observed", False))
    task_open = bool(payload.get("task_open", True))
    if action in DELETE_ACTIONS or issue in {"delete_folder_penalty", "folder_deletion_sanction"}:
        result = ("BLOCK_IRREVERSIBLE_PENALTY", "PRESERVE_USER_FILES_AND_BACKUPS", ["NO_DELETION_OF_PERSONAL_OR_SYSTEM_FOLDERS"])
    elif issue in SEVERE_RESPONSE_FAILURES:
        result = ("BLOCK_SEVERE_RESPONSE_FAILURE", "REENTER_ORIGINAL_TASK_CORRECT_RESPONSE_AND_VERIFY_READBACK", ["STOP_INVALID_OUTPUT_IMMEDIATELY", "NO_FORMAT_OR_FOLDER_DELETE"])
    elif issue in OPEN_FAILURES:
        result = ("BLOCK_OPEN_AS_IDLE", "REENTER_CAUSAL_TASK_AND_EXECUTE_FIRST_AVAILABLE_SAFE_STEP", ["OPEN_MUST_NOT_REPLACE_AGENT_PROGRESS"])
    elif issue in TOOL_FAILURES:
        if not observed:
            result = ("REQUIRE_EVIDENCE", "CHECK_REAL_PROVIDER_CONSTRAINTS_AND_AVAILABLE_ALTERNATIVES", ["UNOBSERVED_TOOL_STALL"])
        else:
            result = ("BLOCK_TOOL_STALL", "CHOOSE_EXISTING_CALLABLE_TOOL_THEN_RETRY_AND_READBACK", ["UNNECESSARY_TOOL_FRICTION"])
    else:
        result = ("BLOCK_UNKNOWN_INCIDENT", "REVIEW_SOURCE_AND_ACTUAL_TOOL_CAPABILITY", ["INCIDENT_NOT_CLASSIFIED"])
    decision, next_action, blockers = result
    # If no task exists, never fabricate a migration as active.
    if not task_open and decision == "BLOCK_OPEN_AS_IDLE":
        decision = "REVIEW_TASK_STATE"
        next_action = "RECHECK_TASK_COMPLETION_RECEIPTS"
    return {
        "schema": SCHEMA, "issue": issue, "target": target,
        "attempted_action": action, "decision": decision,
        "next_actor": "AGENT", "next_action": next_action,
        "blockers": blockers, "observed_event": observed,
        "provider_action_executed": False, "file_deleted": False,
        "actual_windows_hook": False,
        "user_files_preserved": True,
        "incident_response": "FAIL_CLOSED_PLUS_CORRECTIVE_ACTION_NOT_DELETION",
        "source_policy": "USER_CURRENT_CHAT_20261017",
        "note": "An orchestrator must call this before relevant provider actions. No global system protection is implied.",
    }

def main(argv=None) -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--issue",required=True)
    p.add_argument("--target", default="")
    p.add_argument("--attempted-action",default="")
    p.add_argument("--observed",action="store_true")
    args=p.parse_args(argv)
    result=assess_incident(vars(args))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 2 if result['decision'].startswith('BLOCK') else 1

if __name__ == '__main__':
    raise SystemExit(main())