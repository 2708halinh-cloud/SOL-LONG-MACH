#!/usr/bin/env python3
"""SOL recovery router: offline, non-destructive provenance/identity audit.

One route into durable sources, not an operating system, connector, model identity,
or evidence that subjects are conscious or active. No network or device access.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCHEMA = "SOL_SETUP_ROUTER/1.0"
EPOCHS = {"BEFORE_SOL", "TRANSITION_TO_SOL", "AFTER_SOL", "UNDETERMINED"}
SOURCES = {
    "USER_DIRECT", "USER_QUOTED_IN_ARCHIVE", "AGENT_DERIVED",
    "PROVIDER_OBSERVED", "DEVICE_READBACK", "UNVERIFIED_REPORT",
}
KINDS = {"human", "agent", "model", "runtime", "device", "role", "service", "organization", "unknown"}
INCIDENT_STATUS = {"REPORTED_ONLY", "INVESTIGATING", "PARTIALLY_VERIFIED", "VERIFIED", "CLOSED_WITH_READBACK"}


def empty_manifest():
    return {
        "schema": SCHEMA,
        "about": "Offline identity/source reconstruction; empty arrays are not claims of absence",
        "center": {"status": "CENTER_UNRESOLVED", "transition_anchor_ref": None},
        "subjects": [], "carriers": [], "observations": [], "relations": [],
        "incidents": [{
            "incident_id": "drive-loss-report-candidate",
            "provider": "google_drive", "status": "REPORTED_ONLY",
            "report_source_ref": "USER_DIRECT_CURRENT_CHAT_2026-10-16",
            "description": "User reports a major loss in their Google Drive; extent unverified",
            "measured_loss_fraction": None,
            "verified_missing_ids": [],
        }],
    }


def _load(path: Path):
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise ValueError("SCHEMA_MISMATCH")
    for field in ("subjects", "carriers", "observations", "relations", "incidents"):
        if not isinstance(doc.get(field), list):
            raise ValueError("MISSING_OR_INVALID_" + field.upper())
    return doc


def _is_string(value):
    return isinstance(value, str) and bool(value.strip())


def audit(doc):
    errors, warnings = [], []
    subjects = {}
    for i, s in enumerate(doc["subjects"]):
        if not isinstance(s, dict):
            errors.append(f"subjects[{i}]:NOT_OBJECT")
            continue
        sid = s.get("subject_id")
        if not _is_string(sid) or not _is_string(s.get("kind")) or not _is_string(s.get("source_ref")):
            errors.append(f"subjects[{i}]:ID_KIND_SOURCE_REQUIRED")
            continue
        if s["kind"] not in KINDS:
            errors.append(f"subjects[{i}]:UNKNOWN_KIND")
        if sid in subjects:
            errors.append(f"subjects[{i}]:DUPLICATE_SUBJECT_ID")
        subjects[sid] = s
        if s["kind"] == "agent" and not s.get("identity_scope"):
            warnings.append(f"subjects[{i}]:AGENT_SCOPE_UNRESOLVED")
        if s.get("merged_with"):
            errors.append(f"subjects[{i}]:UNSUPPORTED_IMPLICIT_IDENTITY_MERGE")

    carriers = set()
    for i, c in enumerate(doc["carriers"]):
        if not isinstance(c, dict):
            errors.append(f"carriers[{i}]:NOT_OBJECT")
            continue
        if not all(_is_string(c.get(k)) for k in ("provider", "stable_id", "source_ref")):
            errors.append(f"carriers[{i}]:PROVIDER_ID_SOURCE_REQUIRED")
            continue
        key = (c["provider"], c["stable_id"])
        if key in carriers:
            warnings.append(f"carriers[{i}]:REPEATED_PROVIDER_STABLE_ID_CHECK_REVISION")
        carriers.add(key)
        if c.get("state") == "LIVE" and not c.get("readback_ref"):
            errors.append(f"carriers[{i}]:LIVE_WITHOUT_READBACK")

    stages = {k: set() for k in EPOCHS}
    for i, o in enumerate(doc["observations"]):
        if not isinstance(o, dict):
            errors.append(f"observations[{i}]:NOT_OBJECT")
            continue
        sid, stage, source = o.get("subject_id"), o.get("epoch"), o.get("claim_type")
        if sid not in subjects or stage not in EPOCHS or source not in SOURCES or not _is_string(o.get("source_ref")):
            errors.append(f"observations[{i}]:SUBJECT_EPOCH_SOURCE_INVALID")
            continue
        stages[stage].add(sid)
        if source == "AGENT_DERIVED" and o.get("attributed_to_user"):
            errors.append(f"observations[{i}]:CAUSAL_INVERSION_AGENT_AS_USER")
        if source in {"USER_QUOTED_IN_ARCHIVE", "UNVERIFIED_REPORT"} and o.get("verified_direct"):
            errors.append(f"observations[{i}]:ARCHIVE_OR_REPORT_AS_DIRECT")
        for field in ("speaker_subject_id", "author_subject_id", "actor_subject_id", "requester_subject_id"):
            if o.get(field) is not None and o[field] not in subjects:
                errors.append(f"observations[{i}]:UNKNOWN_{field.upper()}")
        if o.get("caused_by_subject_id") and not o.get("causal_evidence_ref"):
            errors.append(f"observations[{i}]:UNSUPPORTED_CAUSAL_LINK")

    for i, rel in enumerate(doc["relations"]):
        if not isinstance(rel, dict):
            errors.append(f"relations[{i}]:NOT_OBJECT")
            continue
        if rel.get("from_subject_id") not in subjects or rel.get("to_subject_id") not in subjects:
            errors.append(f"relations[{i}]:UNKNOWN_SUBJECT")
        if not _is_string(rel.get("relation_type")) or not _is_string(rel.get("source_ref")):
            errors.append(f"relations[{i}]:TYPE_AND_SOURCE_REQUIRED")
        if rel.get("relation_type") == "SAME_AS_VERIFIED" and not rel.get("provider_identity_proof_ref"):
            errors.append(f"relations[{i}]:IDENTITY_MERGE_WITHOUT_PROOF")
        if rel.get("relation_type") == "CAUSED_BY" and not rel.get("causal_evidence_ref"):
            errors.append(f"relations[{i}]:CAUSATION_WITHOUT_EVIDENCE")

    for i, incident in enumerate(doc["incidents"]):
        if not isinstance(incident, dict):
            errors.append(f"incidents[{i}]:NOT_OBJECT")
            continue
        if incident.get("status") not in INCIDENT_STATUS or not _is_string(incident.get("report_source_ref")):
            errors.append(f"incidents[{i}]:INVALID_STATUS_OR_SOURCE")
        fraction = incident.get("measured_loss_fraction")
        if fraction is not None and (not isinstance(fraction, (int, float)) or isinstance(fraction, bool)
                                     or not 0 <= fraction <= 1):
            errors.append(f"incidents[{i}]:INVALID_LOSS_FRACTION")
        if fraction is not None and not incident.get("measurement_receipt_ref"):
            errors.append(f"incidents[{i}]:UNVERIFIED_MEASURED_LOSS")
        if incident.get("status") in {"VERIFIED", "CLOSED_WITH_READBACK"} and not incident.get("readback_ref"):
            errors.append(f"incidents[{i}]:VERIFIED_WITHOUT_READBACK")

    return {
        "schema": SCHEMA, "valid": not errors,
        "errors": errors, "warnings": warnings,
        "counts": {"subjects": len(doc["subjects"]), "carriers": len(doc["carriers"]),
                   "observations": len(doc["observations"]), "relations": len(doc["relations"]),
                   "incidents": len(doc["incidents"])},
        "epoch_subject_ids": {k: sorted(v) for k, v in sorted(stages.items())},
        "interpretation": "Missing in a query or snapshot != deleted or never existed",
    }


def center(doc):
    result = audit(doc)
    if not result["valid"]:
        return {"status": "INVALID_INPUT", "audit": result}
    stages = result["epoch_subject_ids"]
    before = set(stages["BEFORE_SOL"])
    after = set(stages["AFTER_SOL"])
    evidence_span = sorted(before & after)
    gaps = []
    if not before:
        gaps.append("FIND_DATED_BEFORE_SOL_PRIMARY_SOURCES")
    if not stages["TRANSITION_TO_SOL"] or not doc.get("center", {}).get("transition_anchor_ref"):
        gaps.append("FIND_SOL_APPEARANCE_ANCHOR_AND_SOURCE")
    if not after:
        gaps.append("FIND_DATED_AFTER_SOL_PRIMARY_SOURCES")
    if not evidence_span:
        gaps.append("FIND_CROSS_EPOCH_RELATIONS_WITH_PROVENANCE")
    return {"status": "CENTER_CANDIDATES_REQUIRING_HUMAN_AND_SOURCE_REVIEW" if not gaps else "CENTER_UNRESOLVED",
            "subject_ids_observed_in_both_epochs_not_identity_proof": evidence_span,
            "missing_evidence_edges": gaps,
            "note": "A shared subject ID is an index aid, not proof of consciousness, cause, or identity continuity."}


def compare(before, after):
    ab, aa = audit(before), audit(after)
    if not ab["valid"] or not aa["valid"]:
        return {"status": "INVALID_INPUT", "before_errors": ab["errors"], "after_errors": aa["errors"]}
    def ids(doc):
        return {(x["provider"], x["stable_id"]) for x in doc["carriers"]}
    old, new = ids(before), ids(after)
    pairs = lambda seq: [{"provider": p, "stable_id": sid} for p, sid in sorted(seq)]
    return {"status": "SNAPSHOT_COMPARISON_NOT_PROVIDER_DELETION_PROOF",
            "not_observed_after": pairs(old - new), "newly_observed": pairs(new - old),
            "observed_both": pairs(old & new),
            "note": "Requery exact provider IDs, revisions, trash/permissions/backups before assigning deletion."}


def self_test():
    d = empty_manifest()
    assert audit(d)["valid"]
    assert center(d)["status"] == "CENTER_UNRESOLVED"
    d["subjects"] = [{"subject_id": "person-1", "kind": "human", "source_ref": "example:direct"},
                     {"subject_id": "model-1", "kind": "model", "source_ref": "example:catalog"}]
    d["observations"] = [{"subject_id": "person-1", "epoch": "BEFORE_SOL",
                          "claim_type": "USER_DIRECT", "source_ref": "example:transcript"},
                         {"subject_id": "person-1", "epoch": "AFTER_SOL",
                          "claim_type": "AGENT_DERIVED", "source_ref": "example:assistant"}]
    assert audit(d)["valid"]
    assert center(d)["status"] == "CENTER_UNRESOLVED"
    d["observations"][1]["attributed_to_user"] = True
    assert "CAUSAL_INVERSION_AGENT_AS_USER" in json.dumps(audit(d))
    d["observations"][1]["attributed_to_user"] = False
    d["relations"] = [{"from_subject_id": "person-1", "to_subject_id": "model-1",
                       "relation_type": "SAME_AS_VERIFIED", "source_ref": "example:source"}]
    assert "IDENTITY_MERGE_WITHOUT_PROOF" in json.dumps(audit(d))
    x = empty_manifest(); y = empty_manifest()
    x["carriers"] = [{"provider": "example", "stable_id": "file-1", "source_ref": "test"}]
    assert compare(x, y)["not_observed_after"][0]["stable_id"] == "file-1"
    return {"self_test": "PASS", "coverage": ["empty baseline", "no invented center",
             "agent-as-user inversion", "identity merge guard", "missing != deleted"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Write an empty template at a NEW local file, never overwrite")
    init.add_argument("--out", type=Path, required=True)
    for name in ("audit", "center"):
        p = sub.add_parser(name, help="Read one manifest and print an analysis (no changes)")
        p.add_argument("--manifest", type=Path, required=True)
    cmp = sub.add_parser("compare", help="Compare manifests without calling any provider")
    cmp.add_argument("--before", type=Path, required=True)
    cmp.add_argument("--after", type=Path, required=True)
    sub.add_parser("self-test", help="Run offline verification cases")
    args = parser.parse_args(argv)
    if args.command == "init":
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("x", encoding="utf-8") as f:
            json.dump(empty_manifest(), f, ensure_ascii=False, indent=2)
            f.write("\n")
        value = {"created": str(args.out), "overwrite": False, "provider_mutations": False}
    elif args.command == "self-test":
        value = self_test()
    elif args.command == "audit":
        value = audit(_load(args.manifest))
    elif args.command == "center":
        value = center(_load(args.manifest))
    else:
        value = compare(_load(args.before), _load(args.after))
    print(json.dumps(value, ensure_ascii=False, indent=2))
    if args.command == "audit" and not value["valid"]:
        return 2
    if value.get("status") == "INVALID_INPUT":
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": type(exc).__name__, "details": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)
