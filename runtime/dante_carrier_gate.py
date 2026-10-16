#!/usr/bin/env python3
"""DANTE historical-carrier gate: a Drive 404 never proves source deletion."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

CONFIG = "CONFIG_SOL/DANTE_SOURCE_RECONCILIATION_CURRENT.json"
SKILL_SNAPSHOT = "PLATFORM_SYNC/CURRENT/installed_skill_bodies/skills_270_286.json"
REQUIRED_ROLES = ("DANTE_ROOT", "SOURCE_MODEL", "README", "MACHINE_MODEL", "PACKAGE", "CONFIG_SOL_BIND")
SCHEMA = "SOL_DANTE_CARRIER_RECONCILIATION/1.0"


def audit(root: Path, *, availability: dict[str, str] | None = None) -> dict:
    """Select the next supported action, without inventing a live provider or file."""
    base = root.resolve()
    config_path = (base / CONFIG).resolve()
    snapshot_path = (base / SKILL_SNAPSHOT).resolve()
    if not config_path.is_relative_to(base) or not snapshot_path.is_relative_to(base):
        raise ValueError("SOURCE_PATH_ESCAPES_ROOT")
    if not config_path.is_file():
        raise ValueError("CONFIG_SOURCE_MISSING")
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    if payload.get("schema") != SCHEMA:
        raise ValueError("DANTE_CONFIG_SCHEMA_INVALID")
    records = payload.get("carriers") or []
    by_role = {x.get("role"): x for x in records}
    if len(by_role) != len(records) or set(by_role) != set(REQUIRED_ROLES):
        raise ValueError("DANTE_SOURCE_ROLES_INCOMPLETE")
    results = []
    for role in REQUIRED_ROLES:
        rec = by_role[role]
        if not rec.get("source_drive_id") or rec.get("source_deleted") is not None:
            raise ValueError("DANTE_SOURCE_HISTORY_MUST_NOT_BE_FABRICATED")
        status = (availability or {}).get(role, "HTTP_404")
        if status not in {"HTTP_404", "READ_OK", "PERMISSION_DENIED", "UNKNOWN"}:
            raise ValueError("INVALID_PROVIDER_OBSERVATION")
        if status == "READ_OK":
            state, next_step = "PROVIDER_READ_REPORTED_UNVERIFIED", "VERIFY_EXACT_ID_PARENT_AND_PROVIDER_REVISION"
        elif status == "HTTP_404":
            state, next_step = "HISTORICAL_ID_NOT_ACCESSIBLE", "LOOKUP_OTHER_CARRIER_WITH_PROVENANCE"
        else:
            state, next_step = "PROVIDER_ACCESS_NOT_PROVEN", "RECHECK_AUTH_AND_EXACT_PROVIDER_ID"
        results.append({"role": role, "source_id": rec["source_drive_id"],
                        "provider_observation": status, "state": state,
                        "source_deleted": None, "next_step": next_step})
    skill_exists = snapshot_path.is_file()
    skill_verified = False
    if skill_exists:
        entries = json.loads(snapshot_path.read_text(encoding="utf-8"))
        candidates = [x for x in entries if "dante-am-duong-su-router" in x.get("uri", "")]
        original_ids = {x["source_drive_id"] for x in records}
        skill_verified = any(all(i in c.get("content", "") for i in original_ids) for c in candidates)
    live = sum(x["provider_observation"] == "READ_OK" for x in results)
    return {
        "schema": "SOL_DANTE_404_REENTRY_GATE/1.0",
        "old_incident_scope": "2026-10-16_USER_SCREENSHOT_AND_LIVE_PROVIDER_RECHECK",
        "carriers": results, "accessible_reported_count": live,
        "not_accessible_count": sum(x["provider_observation"] == "HTTP_404" for x in results),
        "skill_snapshot_exists": skill_exists,
        "skill_snapshot_covers_historical_ids": skill_verified,
        "skill_snapshot_sha256": hashlib.sha256(snapshot_path.read_bytes()).hexdigest() if skill_exists else None,
        "next_action": ("VERIFY_LIVE_PROVIDER_IDS" if live
                        else "RECOVER_ROUTER_SEMANTICS_FROM_GITHUB_SNAPSHOT"
                        if skill_verified else "SEARCH_AUTHORIZED_SOURCE_CARRIERS"),
        "deleted_source_conclusion": None,
        "repair_target": "CONFIG_SOL/DANTE_SOURCE_RECONCILIATION_CURRENT.json",
        "external_drive_data_recovered": False,
        "scope": "EVIDENCE_TRIAGE_NOT_PROVIDER_RESTORATION",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="DANTE source-404 reentry guard")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(audit(args.repo_root), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
