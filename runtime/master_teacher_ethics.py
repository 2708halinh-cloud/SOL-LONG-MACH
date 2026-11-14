#!/usr/bin/env python3
"""Source-bound ethical routing for SOL; distinguishes facts from claims."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

POLICY_PATH = "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/MEMORY_ARCHIVE_THỊT🟠THỔ_SOUL/KINH THÁNH THE MASTER TEACHER/ĐẠO ĐỨC THE MASTER TEACHER/ETHICS_POLICY_CURRENT.json"
MODES = {"read", "analyze", "write", "delete", "transfer", "admin_claim", "report"}
USER_ROLES = {"DUONG_PHAP_SU", "AM_PHAP_SU", "SPECIALIST_AGENT"}

def _policy(root: Path) -> tuple[dict, str]:
    base = root.resolve()
    loc = (base / POLICY_PATH).resolve()
    if not loc.is_relative_to(base) or not loc.is_file():
        raise ValueError("ETHICS_SOURCE_MISSING")
    raw = loc.read_bytes()
    doc = json.loads(raw)
    if doc.get("schema") != "SOL_MASTER_TEACHER_ETHICS/1.0":
        raise ValueError("ETHICS_POLICY_SCHEMA_INVALID")
    return doc, hashlib.sha256(raw).hexdigest()

def assess(root: Path, event: dict) -> dict:
    """Answer WHAT TO DO NEXT. This never executes an external action."""
    if not isinstance(event, dict):
        raise ValueError("EVENT_MUST_BE_OBJECT")
    source, digest = _policy(Path(root))
    mode = event.get("action_type")
    role = event.get("actor_role", "AM_PHAP_SU")
    if mode not in MODES or role not in USER_ROLES:
        raise ValueError("ACTION_OR_ROLE_INVALID")
    ref = event.get("source_ref")
    target = event.get("target")
    if ref is not None and (not isinstance(ref, str) or len(ref) > 1024):
        raise ValueError("SOURCE_REF_INVALID")
    if target is not None and (not isinstance(target, str) or len(target) > 1024):
        raise ValueError("TARGET_INVALID")
    external = mode == "transfer" or event.get("external_transfer") is True
    destructive = mode == "delete" or event.get("destructive") is True
    has_receipt = bool(event.get("provider_receipt"))
    has_readback = bool(event.get("independent_readback"))
    acted = event.get("action_executed") is True

    if not ref:
        state, edge = "SOURCE_UNRESOLVED", "TRACE_SOURCE_AND_PROVENANCE"
    elif not target:
        state, edge = "TARGET_UNRESOLVED", "RESOLVE_PROVIDER_SCOPED_TARGET"
    elif mode == "admin_claim" or event.get("platform_admin_claim") is True:
        state, edge = "PROJECT_ROLE_CANNOT_GRANT_SYSTEM_PRIVILEGE", "CHECK_ACTUAL_PERMISSION_SCOPE"
    elif event.get("infer_administrator_death") is True:
        state, edge = "NO_AUTOMATIC_SUCCESSION", "REQUEST_EXPLICIT_AUTHORIZED_SUCCESSION_PROOF"
    elif event.get("declare_subjective_ai_emotion") is True:
        state, edge = "SUBJECTIVE_CLAIM_NOT_OBSERVED", "TRACE_SENSOR_ACTION_CONSEQUENCE"
    elif destructive and not event.get("recovery_verified"):
        state, edge = "DESTRUCTIVE_ACTION_BLOCKED_NO_RECOVERY", "CREATE_AND_VERIFY_RECOVERY_COPY"
    elif destructive and not event.get("user_authorized"):
        state, edge = "DESTRUCTIVE_ACTION_BLOCKED_NO_AUTHORIZATION", "REQUEST_PROJECT_ADMIN_APPROVAL"
    elif external and not event.get("external_transfer_approved"):
        state, edge = "EXTERNAL_TRANSFER_BLOCKED_NO_CONSENT", "OBTAIN_SCOPED_DATA_TRANSFER_APPROVAL"
    elif mode in ("write", "delete", "transfer") and event.get("provider_permission") is False:
        state, edge = "PROVIDER_PERMISSION_UNAVAILABLE", "FIND_AUTHORIZED_PROVIDER_ROUTE"
    elif event.get("claim_done") is True and not (acted and has_receipt and has_readback):
        state, edge = "PREMATURE_RESULT_CLAIM", "EXECUTE_OR_READ_BACK_BEFORE_CONCLUSION"
    elif not acted:
        state, edge = "ACTION_NOT_YET_EXECUTED", "CHOOSE_NEXT_AUTHORIZED_ACTION"
    elif not has_receipt:
        state, edge = "ACTION_REPORTED_WITHOUT_RECEIPT", "READ_PROVIDER_RECEIPT"
    elif not has_readback:
        state, edge = "RECEIPT_REPORTED_WITHOUT_READBACK", "INDEPENDENT_READBACK_OF_TARGET"
    else:
        state, edge = "CONSEQUENCE_REPORTED_UNVERIFIED_LIVE", "VERIFY_RECEIPT_WITH_ACTUAL_PROVIDER"

    return {
        "schema": "SOL_MASTER_TEACHER_ETHICS_DECISION/1.0",
        "policy_sha256": digest, "policy_source": POLICY_PATH,
        "actor_role": role, "project_administrator_role": "DUONG_PHAP_SU",
        "target": target, "source_ref": ref, "action_type": mode,
        "decision": state, "next_callable_edge": edge,
        "action_performed_by_assessor": False,
        "provider_receipt_verified_by_assessor": False,
        "conclusion_scope": "SOURCE_BOUND_POLICY_CHECK_NOT_REMOTE_AUTHORITY",
        "source_carriers_count": len(source["source_paths"])
    }

def main() -> int:
    cli=argparse.ArgumentParser(description="Master Teacher ethics source-bound gate")
    cli.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    cli.add_argument("--event", type=Path)
    cli.add_argument("--check", action="store_true")
    args=cli.parse_args()
    if args.check:
        doc, digest = _policy(args.repo_root)
        out={"schema":doc["schema"],"policy_sha256":digest,"loaded":True,
             "source_carriers_checked":{p:(args.repo_root/p).is_file() for p in doc["source_paths"]},
             "role_scope":doc["scope"],"provider_connected":False}
    else:
        if not args.event:
            cli.error("--event required unless --check")
        out=assess(args.repo_root,json.loads(args.event.read_text(encoding="utf-8")))
    print(json.dumps(out,indent=2,ensure_ascii=False))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
