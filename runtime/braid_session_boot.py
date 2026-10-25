#!/usr/bin/env python3
"""Invoke the source-local BRAID proof on every SOL session entry when called.

This is an actual subprocess adapter, not an inference simulation and not a
claim that ChatGPT automatically runs GitHub files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_RUNTIME = Path(r"G:\OS_Workspace\TESSERACT_OS\runtime")
PROOF_NAME = "prove_braid_actual_20261020.py"
REQUIRED_FORCES = {"THAM", "SAN", "SI", "MAN", "NGHI", "AC_KIEN"}
REQUIRED_ROUTES = {
    "PRESERVE_SOURCE_AND_TRACE_PARENT_GRAPH",
    "CHECK_REVERSIBLE_ALTERNATIVES_AND_SNAPSHOT",
    "VERIFY_SOURCE_RECEIPT_AND_CAUSAL_HISTORY",
    "PRESERVE_PARALLEL_ACTION_PATHS",
    "RETAIN_NECESSARY_CARRIER_WHILE_BUILDING_ALTERNATIVES",
    "TEST_AVAILABLE_AUTHORIZED_ALTERNATES",
    "CHECK_COMPANION_CONSEQUENCES_BEFORE_CHOICE",
}


def _receipt_verified(path: str, sha256: str | None = None) -> bool:
    """Validate real receipt bytes; do not create a receipt on failure."""
    if not isinstance(path, str) or not path:
        return False
    p = Path(path)
    if not p.is_file():
        return False
    try:
        data = p.read_bytes()
        json.loads(data.decode("utf-8-sig"))
        if sha256 is not None and hashlib.sha256(data).hexdigest() != sha256:
            return False
        return True
    except (OSError, UnicodeError, ValueError, TypeError):
        return False


def verify_run(proof: dict) -> dict:
    """The proof payload is only trusted for fields independently checked."""
    six = proof.get("six_forces") or {}
    plural = proof.get("plural") or {}
    active = six.get("active")
    routes = six.get("selected_routes")
    chosen = plural.get("selected_routes")
    checks = {
        "context_rejected": proof.get("missing_context_rejected") is True,
        "rejected_no_receipt": proof.get("rejected_request_did_not_create_receipt") is True,
        "six_forces_examined": six.get("all_six_examined") is True
            and isinstance(active, list) and set(active) == REQUIRED_FORCES
            and len(active) == 6,
        "braid_route": six.get("gate_next_edge") == "BRAID_PARALLEL_ACTIONS",
        "source_unchanged_reported": six.get("source_sha256_unchanged") is True,
        "no_mutation_reported": six.get("mutation_executed") is False,
        "all_paths_selected": isinstance(routes, list)
            and REQUIRED_ROUTES.issubset(set(routes)),
        "plural_paths_selected": isinstance(chosen, list)
            and {"PRESERVE_PARALLEL_ACTION_PATHS",
                 "RETAIN_NECESSARY_CARRIER_WHILE_BUILDING_ALTERNATIVES",
                 "TEST_AVAILABLE_AUTHORIZED_ALTERNATES"}.issubset(set(chosen)),
        "six_receipt_source_readback_reported": six.get("receipt_readback_ok") is True,
        "plural_receipt_source_readback_reported": plural.get("receipt_readback_ok") is True,
        "six_receipt_actual_bytes": _receipt_verified(
            six.get("receipt_path"), six.get("receipt_sha256")),
        "plural_receipt_actual_bytes": _receipt_verified(plural.get("receipt_path")),
    }
    return {
        "session_braid_validated": all(checks.values()),
        "checks": checks,
        "six_receipt_path": six.get("receipt_path"),
        "plural_receipt_path": plural.get("receipt_path"),
        "scope_from_source": proof.get("scope"),
        "cloud_host_wiring_from_source": proof.get("cloud_host_wiring"),
    }


def run(runtime_root: Path = DEFAULT_RUNTIME, *, timeout: int = 120) -> dict:
    script = runtime_root / PROOF_NAME
    if not script.is_file():
        return {
            "session_braid_validated": False,
            "execution": "NOT_RUN_SOURCE_SCRIPT_UNREACHABLE",
            "script": str(script),
        }
    try:
        completed = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(runtime_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "session_braid_validated": False,
            "execution": "NOT_CONFIRMED",
            "error_type": type(exc).__name__,
            "script": str(script),
        }
    if completed.returncode:
        return {
            "session_braid_validated": False,
            "execution": "PROOF_SCRIPT_NONZERO_EXIT",
            "exit_code": completed.returncode,
            "script": str(script),
        }
    try:
        proof = json.loads(completed.stdout)
        if not isinstance(proof, dict):
            raise ValueError("not an object")
    except (ValueError, TypeError):
        return {
            "session_braid_validated": False,
            "execution": "UNREADABLE_PROOF_STDOUT",
            "script": str(script),
        }
    result = verify_run(proof)
    result["execution"] = "REAL_LOCAL_SUBPROCESS_FINISHED"
    result["script"] = str(script)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    result = run(args.runtime_root, timeout=args.timeout)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["session_braid_validated"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
