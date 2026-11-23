"""RAM-L1-MEMORY: deterministic parallel orchestration with evidence receipts.

This is a local orchestration scaffold, not a replacement for platform Memory or
an autonomous background service. Call process_signal() when a signal arrives.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
import time
from typing import Any, Callable, Iterable, Mapping, Optional


@dataclass
class BranchResult:
    branch: str
    status: str
    started_at: str
    finished_at: str
    duration_ms: int
    output: Any = None
    error: Optional[str] = None
    evidence_sha256: Optional[str] = None


@dataclass
class Receipt:
    receipt_id: str
    signal_sha256: str
    created_at: str
    status: str
    branches: list[BranchResult]
    conflicts: list[str] = field(default_factory=list)
    commit_allowed: bool = False
    verification: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


Branch = Callable[[Mapping[str, Any]], Any]
Verifier = Callable[[Mapping[str, Any], list[BranchResult]], Mapping[str, Any]]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")


def _digest(value: Any) -> str:
    return sha256(_canonical(value)).hexdigest()


def process_signal(
    signal: Mapping[str, Any],
    branches: Mapping[str, Branch],
    *,
    max_workers: int = 4,
    required_branches: Iterable[str] = (),
    verifier: Optional[Verifier] = None,
    commit_requested: bool = False,
    conflict_rules: Optional[Iterable[Callable[[Mapping[str, Any], list[BranchResult]], Optional[str]]]] = None,
) -> Receipt:
    """Run branches concurrently and permit commit only after verification.

    Branches receive the same read-only-by-convention signal mapping. Branch code
    should avoid shared mutable state and return evidence/data, not side effects.
    """
    if not isinstance(signal, Mapping):
        raise TypeError("signal must be a mapping")
    if max_workers < 1:
        raise ValueError("max_workers must be >= 1")

    signal_hash = _digest(signal)
    results: list[BranchResult] = []

    def run_one(name: str, fn: Branch) -> BranchResult:
        start = time.monotonic()
        started_at = _now()
        try:
            output = fn(signal)
            status, error = "success", None
            evidence_hash = _digest(output)
        except Exception as exc:
            output, status, error, evidence_hash = None, "error", f"{type(exc).__name__}: {exc}", None
        return BranchResult(
            branch=name, status=status, started_at=started_at, finished_at=_now(),
            duration_ms=round((time.monotonic() - start) * 1000),
            output=output, error=error, evidence_sha256=evidence_hash
        )

    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="ram-l1") as pool:
        futures = {pool.submit(run_one, name, fn): name for name, fn in branches.items()}
        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda r: r.branch)
    required = set(required_branches)
    by_name = {r.branch: r for r in results}
    conflicts: list[str] = []
    if not results:
        conflicts.append("No branches executed")
    for name in sorted(required):
        if name not in by_name:
            conflicts.append(f"Required branch missing: {name}")
        elif by_name[name].status != "success":
            conflicts.append(f"Required branch failed: {name}")

    for rule in conflict_rules or ():
        try:
            finding = rule(signal, results)
            if finding:
                conflicts.append(str(finding))
        except Exception as exc:
            conflicts.append(f"Conflict rule failed: {type(exc).__name__}: {exc}")

    verification: dict[str, Any] = {"receipt_integrity": True}
    if verifier is not None:
        try:
            verification.update(dict(verifier(signal, results)))
        except Exception as exc:
            verification["verifier_error"] = f"{type(exc).__name__}: {exc}"
            verification["passed"] = False
    else:
        verification["passed"] = False
        verification["reason"] = "No verifier supplied; execution receipts are not domain verification."

    verifier_passed = verification.get("passed") is True
    all_required_ok = not any(c.startswith("Required branch") for c in conflicts)
    commit_allowed = bool(commit_requested and verifier_passed and all_required_ok and not conflicts)

    if conflicts:
        status = "BLOCKED"
    elif verifier_passed and all(r.status == "success" for r in results):
        status = "VERIFIED"
    else:
        status = "PARTIAL"

    receipt_body = {
        "signal_sha256": signal_hash,
        "created_at": _now(),
        "branches": [asdict(r) for r in results],
        "conflicts": conflicts,
        "commit_allowed": commit_allowed,
        "verification": verification,
    }
    receipt_id = sha256(_canonical(receipt_body)).hexdigest()[:20]
    return Receipt(
        receipt_id=receipt_id, signal_sha256=signal_hash,
        created_at=receipt_body["created_at"], status=status,
        branches=results, conflicts=conflicts, commit_allowed=commit_allowed,
        verification=verification,
    )


def write_receipt(receipt: Receipt, path: str) -> None:
    """Persist a JSON receipt. Creates/replaces the specified file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(receipt.to_dict(), f, ensure_ascii=False, indent=2)


def read_receipt(path: str) -> dict[str, Any]:
    """Read back a saved receipt for an independent post-write check."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not data.get("receipt_id") or not data.get("signal_sha256"):
        raise ValueError("Invalid receipt: required identifiers missing")
    return data
