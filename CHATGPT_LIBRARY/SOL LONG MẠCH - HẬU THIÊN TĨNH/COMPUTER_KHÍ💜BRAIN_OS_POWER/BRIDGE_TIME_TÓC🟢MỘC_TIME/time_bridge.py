#!/usr/bin/env python3
"""TIME × SPACE × REALITY: validate an evidence-bound event without contacting providers."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

IDENTITY_INDEX = "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/CORE_PLACES_INDEX_MÁU_🔴_HỎA_REALITY/IDENTITY_PLACES_CORE.json"
SPACE_SOURCE = "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/EARTH_PEOPLE_XƯƠNG🔵THỦY_SPACE/SPACE.json"
STAMP_CLASSES = {"STAMP_OLD", "STAMP_LIVE", "STAMP_BETA"}
SCHEMA = "SOL_TIME_BRIDGE_EVENT/1.0"


def _load(repo_root: Path, rel: str) -> tuple[dict, str]:
    root = repo_root.resolve()
    target = (root / rel).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise ValueError("SOURCE_MISSING_OR_OUT_OF_SCOPE")
    raw = target.read_bytes()
    return json.loads(raw.decode("utf-8")), hashlib.sha256(raw).hexdigest()


def connect(event: dict, repo_root: Path) -> dict:
    """Choose a concrete next edge; supplied observation != live provider verification."""
    if not isinstance(event, dict) or event.get("schema") != SCHEMA:
        raise ValueError("EVENT_SCHEMA_MISMATCH")
    if not event.get("event_id") or not event.get("source_ref"):
        raise ValueError("EVENT_ID_AND_SOURCE_REQUIRED")
    if event.get("stamp_class") not in STAMP_CLASSES:
        raise ValueError("STAMP_CLASS_INVALID")

    index, index_sha = _load(repo_root, IDENTITY_INDEX)
    space_schema, space_sha = _load(repo_root, SPACE_SOURCE)
    if not isinstance(index.get("names"), list) or space_schema.get("stone") != "SPACE":
        raise ValueError("IDENTITY_OR_SPACE_SOURCE_INVALID")

    names = index["names"]
    label = event.get("identity_label", "")
    identity = next((x for x in names if x.get("label") == label), None)
    candidates = [{"label": x["label"], "kind": x["kind"], "source": x.get("source")}
                  for x in names if "SOL" in x.get("label", "").upper() or
                  "SOL" in " ".join(x.get("aliases", [])).upper()]

    bound = event.get("space") or {}
    if not isinstance(bound, dict):
        raise ValueError("SPACE_BINDING_INVALID")
    action = event.get("action")
    receipt = event.get("provider_receipt")
    readback = event.get("readback_ref")
    classification = event["stamp_class"]

    if identity is None:
        state, next_edge = "IDENTITY_NEEDS_RESOLUTION", "SEARCH_REALITY_IDENTITY_INDEX"
    elif event.get("identity_kind") and event["identity_kind"] != identity["kind"]:
        state, next_edge = "IDENTITY_KIND_CONFLICT", "CHECK_SOURCE_ROLE_AND_KIND"
    elif event.get("x_literal") and not event.get("x_reference_frame"):
        state, next_edge = "X_FRAME_NEEDS_SOURCE", "READ_X_REFERENCE_AND_EVENT_EDGES"
    elif not bound.get("provider") or not bound.get("stable_id"):
        state, next_edge = "SPACE_NEEDS_PROVIDER_ID", "QUERY_PROVIDER_FOR_SCOPED_ID"
    elif not bound.get("parent_id") and bound.get("is_root") is not True:
        state, next_edge = "SPACE_NEEDS_PARENT_FRAME", "READ_PARENT_OR_FRAME"
    elif classification == "STAMP_BETA":
        if action or receipt or readback:
            state, next_edge = "BETA_NOT_OBSERVED_ACTION", "SEPARATE_FORECAST_FROM_LIVE_RECEIPT"
        else:
            state, next_edge = "FORECAST_NOT_EXECUTED", "CHECK_CONDITIONS_AND_AVAILABLE_TOOL"
    elif classification == "STAMP_LIVE" and not event.get("observed_at"):
        state, next_edge = "LIVE_OBSERVATION_NEEDS_TIMESTAMP", "FRESH_READ_PROVIDER_TIME_AND_STATE"
    elif classification == "STAMP_OLD" and not event.get("event_time"):
        state, next_edge = "HISTORICAL_EVENT_TIME_NEEDS_SOURCE", "READ_ORIGINAL_EVENT_SOURCE"
    elif bool(action) + bool(receipt) + bool(readback) not in (0, 3):
        state, next_edge = "PARTIAL_ACTION_EVIDENCE", "FIND_RECEIPT_AND_READBACK"
    elif action and receipt and readback:
        state, next_edge = "ACTION_RECORDED_UNVERIFIED_PROVIDER", "VERIFY_PROVIDER_RECEIPT_EXACT_TARGET"
    else:
        state, next_edge = "SCOPED_SPACE_ID_SUPPLIED_UNVERIFIED", "FRESH_READ_PROVIDER_SPACE_BINDING"

    return {
        "schema": "SOL_TIME_SPACE_REALITY_LINK_RESULT/1.0",
        "event_id": event["event_id"], "source_ref": event["source_ref"],
        "identity_label": label, "identity_candidate": identity,
        "identity_candidates_if_ambiguous": candidates if identity is None else [],
        "index_sha256": index_sha, "space_view_sha256": space_sha,
        "stamp_class": classification,
        "x_literal": event.get("x_literal"),
        "x_reference_frame": event.get("x_reference_frame"),
        "event_time": event.get("event_time"),
        "observed_at": event.get("observed_at"),
        "prior_event_id": event.get("prior_event_id"),
        "space_binding_from_input": bound,
        "state": state, "next_callable_edge": next_edge,
        "provider_receipt_verified_live": False,
        "action_performed_by_this_operator": False,
        "conclusion_scope": "OFFLINE_SOURCE_BOUND_VALIDATION_ONLY",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    ap.add_argument("--event", type=Path, required=True)
    args = ap.parse_args()
    out = connect(json.loads(args.event.read_text(encoding="utf-8")), args.repo_root)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
