"""Small, auditable local control-plane core; stdlib only.

This module records evidence and policy decisions. It does not delete source
artifacts, execute arbitrary user commands, or claim access to unavailable
endpoints. Platform adapters must be injected by the host runtime.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class ProbeResult:
    target: str
    status: str
    sha256: str | None
    size_bytes: int | None
    observed_at: float
    detail: str = ""


@dataclass(frozen=True)
class PolicyDecision:
    action: str
    reasons: tuple[str, ...]
    evidence_sha256: str


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


class CoreJournal:
    """Append-only-by-interface SQLite evidence journal with hash chaining."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS journal (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                ts REAL NOT NULL,
                kind TEXT NOT NULL,
                payload TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                entry_hash TEXT NOT NULL UNIQUE
            )""")

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=5)
        db.execute("PRAGMA busy_timeout=5000")
        return db

    def append(self, kind: str, payload: dict[str, Any]) -> str:
        encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":"))
        now = time.time()
        with self._connect() as db:
            row = db.execute(
                "SELECT entry_hash FROM journal ORDER BY seq DESC LIMIT 1"
            ).fetchone()
            previous = row[0] if row else "GENESIS"
            material = f"{now:.6f}\n{kind}\n{encoded}\n{previous}"
            entry_hash = hashlib.sha256(material.encode("utf-8")).hexdigest()
            db.execute(
                "INSERT INTO journal(ts,kind,payload,previous_hash,entry_hash) "
                "VALUES(?,?,?,?,?)",
                (now, kind, encoded, previous, entry_hash),
            )
        return entry_hash

    def verify_chain(self) -> tuple[bool, str]:
        previous = "GENESIS"
        with self._connect() as db:
            rows = db.execute(
                "SELECT seq,ts,kind,payload,previous_hash,entry_hash "
                "FROM journal ORDER BY seq"
            ).fetchall()
        for seq, ts, kind, payload, recorded_previous, recorded_hash in rows:
            if recorded_previous != previous:
                return False, f"chain break at seq={seq}: previous hash mismatch"
            material = f"{ts:.6f}\n{kind}\n{payload}\n{previous}"
            actual = hashlib.sha256(material.encode("utf-8")).hexdigest()
            if actual != recorded_hash:
                return False, f"chain break at seq={seq}: entry hash mismatch"
            previous = recorded_hash
        return True, f"verified {len(rows)} entries"

    def latest_hash(self) -> str:
        with self._connect() as db:
            row = db.execute(
                "SELECT entry_hash FROM journal ORDER BY seq DESC LIMIT 1"
            ).fetchone()
        return row[0] if row else "GENESIS"


def probe_file(path: str | Path) -> ProbeResult:
    target = str(path)
    now = time.time()
    try:
        stat = os.stat(path)
        if not os.path.isfile(path):
            return ProbeResult(target, "NOT_REGULAR_FILE", None, None, now)
        return ProbeResult(target, "OK", sha256_file(path), stat.st_size, now)
    except FileNotFoundError:
        return ProbeResult(target, "MISSING", None, None, now)
    except PermissionError:
        return ProbeResult(target, "DENIED", None, None, now)
    except OSError as exc:
        return ProbeResult(target, "ERROR", None, None, now, str(exc))


def decide(
    probes: Iterable[ProbeResult],
    journal_ok: bool,
    disk_used_percent: float | None = None,
    disk_stop_threshold: float = 90.0,
) -> PolicyDecision:
    """Fail closed for execution, but preserve evidence and allow safe diagnosis."""
    probes = tuple(probes)
    reasons: list[str] = []
    if not journal_ok:
        reasons.append("CORE_JOURNAL_INTEGRITY_FAILURE")
    for probe in probes:
        if probe.status != "OK":
            reasons.append(f"PROBE_{probe.status}:{probe.target}")
    if disk_used_percent is not None and disk_used_percent >= disk_stop_threshold:
        reasons.append("DISK_PRESSURE_STOP")
    action = "HOLD_AND_DIAGNOSE" if reasons else "ALLOW"
    evidence = json.dumps({
        "probes": [asdict(p) for p in probes],
        "journal_ok": journal_ok,
        "disk_used_percent": disk_used_percent,
        "reasons": reasons,
        "action": action,
    }, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return PolicyDecision(action, tuple(reasons),
                          hashlib.sha256(evidence.encode("utf-8")).hexdigest())


def run_cycle(
    journal: CoreJournal,
    targets: Iterable[str | Path],
    disk_used_percent: float | None = None,
    endpoint_probes: dict[str, Callable[[], dict[str, Any]]] | None = None,
) -> PolicyDecision:
    """One explicit cycle. Endpoint probes are injected and never guessed."""
    probes = [probe_file(p) for p in targets]
    endpoint_evidence: dict[str, Any] = {}
    for name, callback in (endpoint_probes or {}).items():
        try:
            endpoint_evidence[name] = {"status": "OK", "result": callback()}
        except Exception as exc:  # boundary: record adapter failure, do not hide it
            endpoint_evidence[name] = {
                "status": "ERROR", "error_type": type(exc).__name__,
                "detail": str(exc)[:500],
            }
            probes.append(ProbeResult(name, "ERROR", None, None, time.time(),
                                      "endpoint adapter failed"))
    chain_ok, chain_detail = journal.verify_chain()
    decision = decide(probes, chain_ok, disk_used_percent)
    journal.append("CONTROL_CYCLE", {
        "probes": [asdict(p) for p in probes],
        "endpoint_evidence": endpoint_evidence,
        "chain_check_before_append": {"ok": chain_ok, "detail": chain_detail},
        "decision": asdict(decision),
    })
    return decision
