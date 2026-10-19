#!/usr/bin/env python3
"""GGDV capability lifecycle: durable artifacts -> rehydrated RAM -> evidence -> ledger.

Python 3.11+ stdlib. Explicit integration required; this does not hook ChatGPT sessions.
SQLite hashes provide tamper detection relative to a trusted manifest/anchor, not
cryptographic signatures, external provider confirmation or permanent immortality.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sqlite3
import threading
from typing import Any, Callable


def canon(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(data: bytes | str) -> str:
    return hashlib.sha256(data.encode('utf-8') if isinstance(data, str) else data).hexdigest()


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_time(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('TIMESTAMP_REQUIRES_TIMEZONE')
    return dt.astimezone(timezone.utc)


def checked_artifact(root: Path, relative: str) -> Path:
    root = root.resolve()
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ValueError('ARTIFACT_PATH_OUTSIDE_ROOT')
    full = root.joinpath(path)
    if any(p.is_symlink() for p in (full, *list(full.parents)[:len(path.parts)])):
        raise ValueError('ARTIFACT_SYMLINK_REFUSED')
    if not full.resolve().is_relative_to(root) or not full.is_file():
        raise ValueError('ARTIFACT_MISSING_OR_OUTSIDE_ROOT:' + relative)
    return full


@dataclass(frozen=True)
class BootResult:
    manifest_digest: str
    artifact_hashes: dict[str, str]
    capabilities: dict[str, dict]
    blackboard: dict[str, Any]
    checkpoint_source: str
    ledger_head: str
    provider_execution_claimed: bool = False


class CapabilityLedger:
    """Attestation ledger and confidence/decay evaluator.

    No network access; no tool execution. A calibration callback is supplied by
    the verified caller and is treated as local simulation, never provider proof.
    """
    DDL = """
    PRAGMA foreign_keys=ON;
    CREATE TABLE IF NOT EXISTS capability_events(
      seq INTEGER PRIMARY KEY AUTOINCREMENT,
      capability_id TEXT NOT NULL,
      kind TEXT NOT NULL,
      payload_json TEXT NOT NULL,
      payload_hash TEXT NOT NULL,
      previous_hash TEXT NOT NULL,
      chain_hash TEXT NOT NULL,
      event_time TEXT NOT NULL);
    CREATE TRIGGER IF NOT EXISTS capability_events_no_update BEFORE UPDATE ON capability_events
      BEGIN SELECT RAISE(ABORT,'CAPABILITY_EVENTS_APPEND_ONLY'); END;
    CREATE TRIGGER IF NOT EXISTS capability_events_no_delete BEFORE DELETE ON capability_events
      BEGIN SELECT RAISE(ABORT,'CAPABILITY_EVENTS_APPEND_ONLY'); END;
    CREATE INDEX IF NOT EXISTS idx_capability_event ON capability_events(capability_id,seq);
    """

    def __init__(self, db_path: str | Path):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.db = sqlite3.connect(str(self.path), check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(self.DDL)

    def close(self):
        self.db.close()

    def head(self) -> str:
        row = self.db.execute('SELECT chain_hash FROM capability_events ORDER BY seq DESC LIMIT 1').fetchone()
        return row[0] if row else 'GENESIS'

    def append(self, capability_id: str, kind: str, payload: dict,
               *, at: datetime | None = None) -> dict:
        if not capability_id or not kind or not isinstance(payload, dict):
            raise ValueError('CAPABILITY_EVENT_INVALID')
        at = at or now_utc()
        if at.tzinfo is None:
            raise ValueError('TIMESTAMP_REQUIRES_TIMEZONE')
        timestamp = at.astimezone(timezone.utc).isoformat()
        body = canon(payload)
        digest = sha(body)
        with self.lock, self.db:
            previous = self.head()
            chain = sha(canon([capability_id, kind, digest, previous, timestamp]))
            cursor = self.db.execute('''INSERT INTO capability_events
                (capability_id,kind,payload_json,payload_hash,previous_hash,chain_hash,event_time)
                VALUES(?,?,?,?,?,?,?)''',
                (capability_id, kind, body, digest, previous, chain, timestamp))
            return {'event_id': cursor.lastrowid, 'event_hash': chain, 'payload_sha256': digest,
                    'previous_hash': previous, 'timestamp': timestamp}

    def verify(self) -> bool:
        previous = 'GENESIS'
        for row in self.db.execute('SELECT * FROM capability_events ORDER BY seq'):
            if sha(row['payload_json']) != row['payload_hash'] or row['previous_hash'] != previous:
                return False
            expected = sha(canon([row['capability_id'], row['kind'], row['payload_hash'],
                                  previous, row['event_time']]))
            if expected != row['chain_hash']:
                return False
            previous = row['chain_hash']
        return True

    def events(self, capability_id: str) -> list[dict]:
        return [dict(row) for row in self.db.execute(
            'SELECT * FROM capability_events WHERE capability_id=? ORDER BY seq', (capability_id,))]

    def record_local_readback(self, capability_id: str, source_path: Path,
                              readback_path: Path, expected_sha256: str,
                              *, at: datetime | None = None) -> dict:
        # Compare source and actual target bytes; HTTP 200 or a declarative flag is insufficient.
        left, right = source_path.read_bytes(), readback_path.read_bytes()
        digest = sha(left)
        if digest != expected_sha256 or sha(right) != digest:
            raise ValueError('READBACK_BYTE_HASH_MISMATCH')
        return self.append(capability_id, 'LOCAL_READBACK_VERIFIED',
                           {'artifact_sha256': digest, 'target_path': str(readback_path),
                            'source_path': str(source_path), 'evidence_kind': 'local_bytes'}, at=at)

    def record_external_reference(self, capability_id: str, receipt_ref: str,
                                  readback_ref: str, *, at: datetime | None = None) -> dict:
        # References are NOT independent attestations. They never mark a remote provider verified.
        if not receipt_ref or not readback_ref:
            raise ValueError('PROVIDER_REFERENCES_REQUIRED')
        return self.append(capability_id, 'EXTERNAL_REFS_UNVERIFIED',
                           {'receipt_ref': receipt_ref, 'readback_ref': readback_ref}, at=at)

    def status(self, capability_id: str, *, at: datetime | None = None,
               half_life_hours: float = 168., threshold: float = .3) -> dict:
        if not self.verify():
            return {'capability_id': capability_id, 'state': 'LEDGER_TAMPERED',
                    'evidence_score': 0.0, 'calibration_due': False}
        if half_life_hours <= 0 or not (0 < threshold < 1):
            raise ValueError('INVALID_DECAY_PARAMETERS')
        rows = self.events(capability_id)
        evidence = [r for r in rows if r['kind'] in {'LOCAL_READBACK_VERIFIED', 'CALIBRATION_OK'}]
        if not evidence:
            return {'capability_id': capability_id, 'state': 'UNVERIFIED',
                    'evidence_score': 0., 'calibration_due': True}
        latest = evidence[-1]
        observed = parse_time(latest['event_time'])
        at = at or now_utc()
        age = max(0, (at.astimezone(timezone.utc) - observed).total_seconds() / 3600)
        # Test evidence is less influential than independent byte-readback evidence.
        base = 1.0 if latest['kind'] == 'LOCAL_READBACK_VERIFIED' else .6
        score = base * math.exp(-math.log(2) * age / half_life_hours)
        last_event = rows[-1] if rows else None
        failed = bool(last_event and last_event['kind'] == 'CALIBRATION_FAILED')
        degraded = failed or score < threshold
        return {'capability_id': capability_id,
                'state': 'DEGRADED' if degraded else ('VERIFIED_LOCAL' if base == 1 else 'CALIBRATED_SIMULATION_ONLY'),
                'evidence_score': round(score, 6), 'calibration_due': degraded,
                'last_verified_at': latest['event_time'], 'evidence_kind': latest['kind'],
                'last_event_hash': last_event['chain_hash']}

    def calibrate(self, capability_id: str, callback: Callable[[], Any],
                  *, at: datetime | None = None) -> dict:
        """Explicit, trusted callback. Simulation/local result, not external action proof."""
        try:
            result = callback()
            if not isinstance(result, dict) or result.get('passed') is not True:
                raise ValueError('CALIBRATION_RESULT_NOT_PASSED')
            result_digest = sha(canon(result))
            receipt = self.append(capability_id, 'CALIBRATION_OK',
                                  {'result_sha256': result_digest, 'scope': 'local_only'}, at=at)
            return {'state': 'CALIBRATED_SIMULATION_ONLY', 'receipt': receipt}
        except Exception as exc:
            receipt = self.append(capability_id, 'CALIBRATION_FAILED',
                                  {'error_class': type(exc).__name__, 'scope': 'local_only'}, at=at)
            return {'state': 'DEGRADED', 'receipt': receipt}


def verify_core_journal(connection: sqlite3.Connection, run_id: str) -> bool:
    try:
        rows = connection.execute('''SELECT step_id, actor, action_type, payload_json,
            provenance_hash, previous_hash, chain_hash FROM journal_entries
            WHERE run_id=? ORDER BY entry_id''', (run_id,)).fetchall()
    except sqlite3.Error:
        return False
    previous = 'GENESIS'
    for step_id, actor, action_type, payload, digest, prev, chain in rows:
        if sha(payload) != digest or prev != previous:
            return False
        expected = sha(canon([run_id, step_id, actor, action_type, digest, previous]))
        if chain != expected:
            return False
        previous = chain
    return True


def rehydrate_checkpoint(db_path: str | Path | None, run_id: str | None,
                         session_id: str) -> tuple[dict, str]:
    blank = {'session_id': session_id, 'turn_id': 0, 'stage': 'INPUT',
             'divergent_pool': [], 'bagua': None, 'selected_hypothesis_id': None,
             'readback_passed': False, 'raw_tool_payload': None, 'scratchpad': {}}
    if not db_path or not run_id or not Path(db_path).is_file():
        return blank, 'FRESH_RAM_NO_CHECKPOINT'
    db = sqlite3.connect(str(db_path))
    try:
        if not verify_core_journal(db, run_id):
            raise ValueError('CORE_JOURNAL_CHAIN_INVALID')
        rows = db.execute('''SELECT full_state_snapshot,checksum FROM checkpoints
            WHERE run_id=? ORDER BY step_index DESC,created_at DESC''', (run_id,)).fetchall()
        for content, checksum in rows:
            if sha(content) != checksum:
                continue
            state = json.loads(content)
            if not isinstance(state, dict):
                continue
            state.update({'session_id': session_id, 'raw_tool_payload': None, 'scratchpad': {},
                          'readback_passed': False,
                          'stage': 'CRITIC' if state.get('bagua') is not None else 'INPUT'})
            return state, 'CHECKPOINT_HASH_MATCH_REQUIRE_FRESH_PROVIDER_READBACK'
        return blank, 'FRESH_RAM_NO_VALID_CHECKPOINT'
    except sqlite3.Error as exc:
        raise ValueError('CORE_JOURNAL_UNREADABLE:' + type(exc).__name__) from None
    finally:
        db.close()


def bootstrap(manifest_path: str | Path, ledger_path: str | Path,
              *, session_id: str, core_db_path: str | Path | None = None,
              run_id: str | None = None) -> BootResult:
    manifest_path = Path(manifest_path)
    data = manifest_path.read_bytes()
    manifest = json.loads(data)
    if manifest.get('schema') != 'GGDV_CAPABILITY_MANIFEST/1.0':
        raise ValueError('MANIFEST_SCHEMA_INVALID')
    root = manifest_path.parent.resolve()
    actual = {}
    for item in manifest.get('artifacts', []):
        relative, digest = item['path'], item['sha256']
        if relative in actual:
            raise ValueError('DUPLICATE_ARTIFACT')
        real = sha(checked_artifact(root, relative).read_bytes())
        if real != digest:
            raise ValueError('ARTIFACT_INTEGRITY_MISMATCH:' + relative)
        actual[relative] = real
    ledger = CapabilityLedger(ledger_path)
    try:
        if not ledger.verify():
            raise ValueError('CAPABILITY_LEDGER_CHAIN_INVALID')
        capability_specs = {item['id']: item for item in manifest.get('capabilities', [])}
        if len(capability_specs) != len(manifest.get('capabilities', [])):
            raise ValueError('DUPLICATE_CAPABILITY_ID')
        for spec in capability_specs.values():
            if not spec.get('artifact_refs') or any(x not in actual for x in spec['artifact_refs']):
                raise ValueError('CAPABILITY_ARTIFACT_REF_INVALID')
        memory, source = rehydrate_checkpoint(core_db_path, run_id, session_id)
        statuses = {key: {**item, 'status': ledger.status(key)} for key, item in capability_specs.items()}
        return BootResult(manifest_digest=sha(data), artifact_hashes=actual,
                          capabilities=statuses, blackboard=memory,
                          checkpoint_source=source, ledger_head=ledger.head())
    finally:
        ledger.close()