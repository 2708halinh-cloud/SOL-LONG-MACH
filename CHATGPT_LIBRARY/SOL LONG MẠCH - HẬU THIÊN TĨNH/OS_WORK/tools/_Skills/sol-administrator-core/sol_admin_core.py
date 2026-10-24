"""Local SOL Administrator core: evidence-first state probes and SQLite journal."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProbeResult:
    source: str
    exists: bool
    sha256: str | None
    bytes: int
    drift: bool
    detail: str


class CoreJournal:
    """Append-only event journal. Hashes are integrity checks, not authentication."""

    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS journal (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts REAL NOT NULL,
                    event_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    entry_hash TEXT NOT NULL
                )
            """)

    def _connect(self):
        db = sqlite3.connect(self.db_path, timeout=5)
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA synchronous=FULL")
        return db

    def append(self, event_type: str, source: str, payload: dict[str, Any]) -> str:
        with self._connect() as db:
            row = db.execute(
                "SELECT entry_hash FROM journal ORDER BY seq DESC LIMIT 1"
            ).fetchone()
            previous = row[0] if row else "GENESIS"
            ts = time.time()
            payload_json = json.dumps(payload, sort_keys=True, ensure_ascii=False)
            canonical = json.dumps(
                [ts, event_type, source, payload_json, previous],
                separators=(",", ":"), ensure_ascii=False
            ).encode("utf-8")
            digest = hashlib.sha256(canonical).hexdigest()
            db.execute(
                """INSERT INTO journal
                   (ts,event_type,source,payload_json,previous_hash,entry_hash)
                   VALUES (?,?,?,?,?,?)""",
                (ts, event_type, source, payload_json, previous, digest),
            )
            return digest

    def verify_chain(self) -> bool:
        with self._connect() as db:
            rows = db.execute(
                """SELECT ts,event_type,source,payload_json,previous_hash,entry_hash
                   FROM journal ORDER BY seq"""
            ).fetchall()
        previous = "GENESIS"
        for ts, event_type, source, payload_json, stored_previous, stored_hash in rows:
            if stored_previous != previous:
                return False
            canonical = json.dumps(
                [ts, event_type, source, payload_json, previous],
                separators=(",", ":"), ensure_ascii=False
            ).encode("utf-8")
            if hashlib.sha256(canonical).hexdigest() != stored_hash:
                return False
            previous = stored_hash
        return True


class Administrator:
    """Fail-closed gate for state snapshots and privileged actions."""

    def __init__(self, journal: CoreJournal):
        self.journal = journal

    def probe_file(self, path: str | Path, expected_sha256: str | None = None) -> ProbeResult:
        p = Path(path)
        if not p.is_file():
            result = ProbeResult(str(p), False, None, 0, expected_sha256 is not None,
                                 "MISSING_SOURCE")
        else:
            data = p.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            drift = expected_sha256 is not None and digest != expected_sha256
            result = ProbeResult(str(p), True, digest, len(data), drift,
                                 "DRIFT" if drift else "OK")
        self.journal.append("STATE_PROBE", str(p), asdict(result))
        return result

    def authorize(self, *, provenance_ok: bool, drift_score: int,
                  journal_integrity_ok: bool, action: str) -> dict[str, Any]:
        allowed = provenance_ok and drift_score == 0 and journal_integrity_ok
        decision = {
            "allowed": allowed,
            "action": action,
            "gate": "PASS" if allowed else "STOP_FORWARD",
            "reasons": [
                reason for condition, reason in (
                    (provenance_ok, "PROVENANCE_MISSING"),
                    (drift_score == 0, "STATE_DRIFT"),
                    (journal_integrity_ok, "JOURNAL_CHAIN_INVALID"),
                ) if not condition
            ],
        }
        self.journal.append("GATE_DECISION", "administrator", decision)
        return decision
