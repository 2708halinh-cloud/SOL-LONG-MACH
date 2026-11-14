#!/usr/bin/env python3
"""Hosted GitHub continuity snapshot independent of Windows, Android and Monid uptime.

This checks observable repository carriers. It does not fabricate provider tokens,
Monid VM activity, physical EEG, or completion of unresolved work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

SOURCE_REFS = (
    "AGENTS.md",
    "CURRENT_RUNTIME/R-000_CURRENT.md",
    "CURRENT_RUNTIME/TASK_RESUME_POINTER.json",
    "CURRENT_RUNTIME/MEMORY_STEWARDSHIP_CURRENT.json",
    "CURRENT_RUNTIME/STAMP_OLD_X_0917_20261016_RESET_GATE.md",
    "CONFIG_SOL/INFINITY_STONES_SYSTEM.md",
    "CONFIG_SOL/TIME_STONE_CORE_CURRENT.json",
    "CONFIG_SOL/SOUL_STONE_CORE_CURRENT.json",
    "CURRENT_RUNTIME/MONID_X66_BINDING_CURRENT.json",
    "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/MEMORY_ARCHIVE_THỊT🟠THỔ_SOUL/BRAINWAVE_REGISTRY/REGISTRY_POLICY.json",
)
OPEN_JOBS = (
    "HOSTINGER_OAUTH_SESSION",
    "AVENGERS_MONID_PROVIDER_RUN_RECONCILIATION",
    "BRAINWAVE_FIVE_LAYER_EVENT_READBACK",
    "TIME_STONE_MISSING_MESSAGE_PROVENANCE",
    "ANDROID_REDMINOTE14_INDEPENDENT_ACCESS",
    "MEMORY_ARCHIVE_CROSS_PLATFORM_RECONCILIATION",
    "TESSERACT_6D_WEB_PUBLICATION",
    "CODEX_DRIVE_ANDROID_SYNC",
)
SCHEMA = "SOL_X66_INDEPENDENT_CONTINUITY_V1"


def fingerprint(root: Path, relative: str) -> dict:
    path = root / relative
    if not path.is_file() or path.is_symlink():
        return {"source_ref": relative, "exists": False, "hash_verified": False}
    data = path.read_bytes()
    return {
        "source_ref": relative,
        "exists": True,
        "hash_verified": True,
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def build(root: Path, timestamp: str, run_id: str, commit_sha: str) -> dict:
    readings = [fingerprint(root, ref) for ref in SOURCE_REFS]
    gaps = [item["source_ref"] for item in readings if not item["exists"]]
    return {
        "schema": SCHEMA,
        "runtime": "GITHUB_HOSTED_UBUNTU_INDEPENDENT_OF_PERSONAL_DEVICES",
        "machine_id_ref": "SOL-X66-MAY-AO",
        "monid_live_machine_exec_proven": False,
        "monid_guest_receipt_verified_on_this_run": False,
        "provider_connections_authenticated_on_this_run": False,
        "source_observations": readings,
        "STAMP_OLD": {
            "historical_source_ref": "CURRENT_RUNTIME/STAMP_OLD_X_0917_20261016_RESET_GATE.md",
            "source_history_overwritten": False,
        },
        "STAMP_LIVE": {
            "observed_at_utc": timestamp,
            "runner": "GITHUB_ACTIONS",
            "run_id": run_id,
            "repo_commit": commit_sha,
            "source_gap_count": len(gaps),
        },
        "STAMP_BETA": {
            "open_source_gaps": gaps,
            "open_jobs": list(OPEN_JOBS),
            "completion_requires_target_readback": True,
        },
        "source_snapshot_complete": len(gaps) == 0,
        "overall_objectives_completed": False,
    }


def atomic_write(path: Path, payload: dict) -> None:
    data = (json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".incoming")
    with tmp.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)
    if path.read_bytes() != data:
        raise RuntimeError("GITHUB_CONTINUITY_READBACK_MISMATCH")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.repo_root.resolve()
    now = datetime.now(timezone.utc).isoformat()
    obj = build(source, now, os.environ.get("GITHUB_RUN_ID", "LOCAL_TEST"),
                os.environ.get("GITHUB_SHA", "UNKNOWN"))
    atomic_write(args.output, obj)
    again = json.loads(args.output.read_text(encoding="utf-8"))
    if again != obj:
        raise RuntimeError("VERIFY_AFTER_WRITE_FAILED")
    print(json.dumps({
        "source_count": len(obj["source_observations"]),
        "source_gaps": obj["STAMP_LIVE"]["source_gap_count"],
        "stamp_live": now,
        "readback": True,
        "all_tasks_done": False,
        "receipt_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    }))
    return 0 if not obj["STAMP_BETA"]["open_source_gaps"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
