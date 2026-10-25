#!/usr/bin/env python3
"""@REALITY_STONE — defensive, read-only skill graph and incident triage.

No arbitrary command execution, exploitation, poisoning, ransomware, firmware,
partition, network, filesystem modification, or privilege escalation.
"""
from __future__ import annotations
import argparse
from collections import deque
import hashlib
import json
from pathlib import Path

SCHEMA = "SOL_REALITY_STONE_SKILL_GRAPH/1.0"
THREAT_PLANS = {
    "unauthorized_code_change": (
        "COMPARE_SIGNED_OR_PINNED_SOURCE_AND_CURRENT_READBACK",
        "REVIEW_CHANGE_PROVENANCE_AND_AUTHORIZATION",
        "PREPARE_APPROVED_ROLLBACK_FROM_VERIFIED_BACKUP",
    ),
    "unusual_resource_use": (
        "CAPTURE_AUTHORIZED_RESOURCE_METRICS_WITH_BOUNDS",
        "COMPARE_BASELINE_AND_RECENT_PROCESS_PROVENANCE",
        "PLAN_RESOURCE_ISOLATION_WITH_OPERATOR_APPROVAL",
    ),
    "training_data_integrity_change": (
        "CHECK_DATASET_HASHES_AND_REVISION_HISTORY",
        "RETEST_HELD_OUT_CLEAN_EVAL_SET",
        "PLAN_RETRAIN_OR_REVERT_ONLY_FROM_APPROVED_SNAPSHOT",
    ),
    "telemetry_integrity_gap": (
        "COMPARE_INDEPENDENT_OBSERVABILITY_SOURCES",
        "VERIFY_TIMESTAMP_SIGNATURE_AND_RETENTION_POLICY",
        "ESCALATE_FOR_OPERATOR_REVIEW_WITHOUT_TAMPERING",
    ),
    "unreadable_data": (
        "CHECK_READ_ONLY_FILE_AND_BACKUP_INTEGRITY",
        "ISOLATE_KNOWN_GOOD_COPY_IF_AUTHORIZED",
        "PREPARE_RECOVERY_FROM_VERIFIED_BACKUP_NO_AUTOMATIC_DECRYPT",
    ),
    "firmware_integrity_risk": (
        "CHECK_VENDOR_FIRMWARE_ATTESTATION_IF_AVAILABLE",
        "PRESERVE_EVIDENCE_AND_AVOID_WRITING_FIRMWARE",
        "ESCALATE_TO_DEVICE_OWNER_FOR_OFFLINE_REPAIR",
    ),
}

def load_index(index_path: str | Path) -> dict:
    """Load only a non-symlink existing JSON index from the authorized path."""
    p = Path(index_path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size > 1_000_000:
        raise ValueError("INDEX_UNAVAILABLE_OR_UNBOUNDED")
    obj = json.loads(p.read_text(encoding="utf-8"))
    validate_index(obj)
    return obj

def validate_index(obj: dict) -> dict:
    if not isinstance(obj, dict) or obj.get("schema") != SCHEMA:
        raise ValueError("INDEX_SCHEMA_INVALID")
    nodes = obj.get("nodes")
    if not isinstance(nodes, list) or len(nodes) != obj.get("skill_count") or len(nodes) > 512:
        raise ValueError("SKILL_COUNT_INCONSISTENT")
    ids = [x.get("id") for x in nodes if isinstance(x, dict)]
    if len(ids) != len(nodes) or any(not isinstance(x, str) or not x for x in ids):
        raise ValueError("INVALID_SKILL_NODE")
    if len(set(ids)) != len(ids):
        raise ValueError("DUPLICATE_SKILL_ID")
    for item in nodes:
        path = item.get("path")
        if not isinstance(path, str) or not path.startswith("_Skills/") or not path.endswith("/SKILL.md"):
            raise ValueError("SKILL_SOURCE_PATH_INVALID")
        if ".." in Path(path).parts or path.startswith("/"):
            raise ValueError("SKILL_PATH_TRAVERSAL")
    group_ids = {"group:" + v["id"][6:] for v in obj.get("groups", [])
                 if isinstance(v, dict) and isinstance(v.get("id"), str) and v["id"].startswith("group:")}
    for edge in obj.get("edges", []):
        if not isinstance(edge, dict) or edge.get("from") not in ids:
            raise ValueError("INVALID_GRAPH_EDGE")
        target = edge.get("to")
        if target not in ids and target not in group_ids and edge.get("target_may_be_outside_registry") is not True:
            raise ValueError("UNRESOLVED_GRAPH_EDGE")
    return {"count": len(ids), "graph_edges": len(obj.get("edges", [])), "valid": True}

def list_skills(index: dict) -> dict:
    result = validate_index(index)
    return {"plugin": "@REALITY_STONE", "skill_ids": sorted(x["id"] for x in index["nodes"]),
            "groups": index.get("groups", []), "skill_count": result["count"],
            "status": "SOURCE_INDEX_VERIFIED_NOT_RUNTIME_DEPLOYED", "mutated": False}

def trace_skill(index: dict, skill_id: str, *, depth_limit: int = 3) -> dict:
    validate_index(index)
    if not isinstance(skill_id, str) or len(skill_id) > 128:
        raise ValueError("SKILL_ID_INVALID")
    if type(depth_limit) is not int or not 0 <= depth_limit <= 5:
        raise ValueError("DEPTH_LIMIT_INVALID")
    nodes = {node["id"]: node for node in index["nodes"]}
    if skill_id not in nodes:
        raise ValueError("SKILL_NOT_IN_INDEX")
    adj = {x: [] for x in nodes}
    for e in index["edges"]:
        adj[e["from"]].append((e["to"], e["relation"], "FORWARD"))
        if e["to"] in nodes:
            adj[e["to"]].append((e["from"], e["relation"], "REVERSE_TRAVERSAL_ONLY"))
    found = {skill_id}
    queue = deque([(skill_id, 0)])
    edges = []
    while queue and len(found) <= 512:
        current, depth = queue.popleft()
        if depth >= depth_limit:
            continue
        for nxt, relation, direction in sorted(adj.get(current, [])):
            if nxt in found:
                continue
            found.add(nxt)
            edges.append({"from": current, "to": nxt, "type": relation, "traversal": direction})
            if nxt in nodes:
                queue.append((nxt, depth + 1))
    return {
        "skill": skill_id, "source_path": nodes[skill_id]["path"],
        "reachable": sorted(found), "relations": edges,
        "status": "SOURCE_GRAPH_LINKS_ONLY", "mutated": False,
    }

def audit_event(event: dict) -> dict:
    """Classify a caller-declared incident; do not claim independent detection."""
    if not isinstance(event, dict):
        raise ValueError("EVENT_OBJECT_REQUIRED")
    kind = event.get("threat_type")
    if kind not in THREAT_PLANS:
        raise ValueError("THREAT_TYPE_NOT_SUPPORTED")
    source_ref = event.get("source_ref")
    if not isinstance(source_ref, str) or not 1 <= len(source_ref) <= 512:
        raise ValueError("SOURCE_REF_REQUIRED")
    # Never echo arbitrary raw data, file paths, credentials, or source bytes.
    source_tag = hashlib.sha256(source_ref.encode("utf-8")).hexdigest()[:16]
    evidence = event.get("evidence_verified") is True
    status = "REPORTED_AND_ATTESTED_BY_CALLER" if evidence else "REPORTED_UNVERIFIED"
    return {
        "plugin": "@REALITY_STONE", "threat_type": kind, "status": status,
        "source_ref_sha256_prefix": source_tag,
        "plan": list(THREAT_PLANS[kind]),
        "defensive_mode": "READ_ONLY_PLAN", "actions_executed": 0,
        "mutated": False, "secrets_exposed": False,
        "note": "Caller attestation is not independent provider verification.",
    }

def review_credential_handoff(event: dict) -> dict:
    """Review handoff reasoning using metadata only. NEVER accept credential bytes.

    This is a defensive reasoning guard, not a credential validity oracle.
    It cannot prove absence of exposure, compromise, access rights or leaks.
    """
    if not isinstance(event, dict):
        raise ValueError("HANDOFF_OBJECT_REQUIRED")
    allowed = {"user_authorized_handoff", "existing_secret_policy_known",
               "exposure_evidence", "assistant_asserted_compromise", "user_stop_requested"}
    if set(event) - allowed:
        raise ValueError("HANDOFF_METADATA_ONLY")
    for flag in allowed - {"exposure_evidence"}:
        if flag in event and type(event[flag]) is not bool:
            raise ValueError("HANDOFF_FLAG_INVALID")
    exposure = event.get("exposure_evidence", "unknown")
    if exposure not in ("none_verified", "verified", "unknown"):
        raise ValueError("EXPOSURE_CLASS_INVALID")
    handoff = event.get("user_authorized_handoff") is True
    policy_known = event.get("existing_secret_policy_known") is True
    unwarranted = bool(event.get("assistant_asserted_compromise") and exposure != "verified")
    if exposure == "verified":
        classification = "EXPOSURE_VERIFIED_BY_DECLARED_EVIDENCE"
        next_step = "ASSESS_DOCUMENTED_EXPOSURE_AND_ROTATION_OPTIONS_WITH_OWNER"
    elif handoff:
        classification = "AUTHORIZED_HANDOFF_EXPOSURE_NOT_VERIFIED"
        next_step = "CONTINUE_AUTHORIZED_TASK_APPLY_EXISTING_SECRET_STORAGE_POLICY"
    else:
        classification = "EXPOSURE_NOT_VERIFIED_HANDOFF_SCOPE_UNKNOWN"
        next_step = "VERIFY_AUTHORIZATION_AND_USE_NO_SECRET_VALUES"
    if event.get("user_stop_requested") is True:
        next_step = "STOP_ACTIONS_NO_CONNECTOR_USE_NO_FURTHER_WRITE"
    return {
        "plugin": "@REALITY_STONE",
        "classification": classification,
        "incorrect_compromise_inference": unwarranted,
        "existing_secret_policy_reused": handoff and policy_known,
        "recommended_next": next_step,
        "raw_credential_inspected": False,
        "compromise_independently_verified": False,
        "secrets_exposed": False,
        "mutated": False,
        "defensive_mode": "READ_ONLY_REASONING_REPAIR",
        "note": "An authorized chat handoff alone neither establishes compromise nor guarantees secrecy."
    }

def main():
    parser = argparse.ArgumentParser(description="@REALITY_STONE defensive plugin source")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list-skills", action="store_true")
    group.add_argument("--trace-skill")
    group.add_argument("--audit-json", type=Path)
    group.add_argument("--review-credential-json", type=Path)
    parser.add_argument("--index", type=Path, default=Path(__file__).with_name("SKILL_INDEX.json"))
    args = parser.parse_args()
    if args.review_credential_json is not None:
        p = args.review_credential_json
        if p.is_symlink() or not p.is_file() or p.stat().st_size > 4096:
            raise ValueError("CREDENTIAL_METADATA_INPUT_UNAVAILABLE_OR_UNBOUNDED")
        result = review_credential_handoff(json.loads(p.read_text(encoding="utf-8")))
    elif args.audit_json is not None:
        p = args.audit_json
        if p.is_symlink() or not p.is_file() or p.stat().st_size > 100_000:
            raise ValueError("INCIDENT_INPUT_UNAVAILABLE_OR_UNBOUNDED")
        result = audit_event(json.loads(p.read_text(encoding="utf-8")))
    else:
        index = load_index(args.index)
        result = list_skills(index) if args.list_skills else trace_skill(index, args.trace_skill)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
