#!/usr/bin/env python3
"""GGDV core: Bát Hướng -> STAMP_OLD/LIVE -> validated decision -> STAMP_BETA.

This is an opt-in library for callers to integrate, not a global host intercept.
Python >=3.11, pydantic >=2, jsonschema >=4. Reads/writes only the
explicit SQLite database selected by the caller. Never claims external success.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import re
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator
from jsonschema import Draft202012Validator


def canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def sha256(value: str | bytes) -> str:
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


class Hypothesis(BaseModel):
    id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    divergent_angle: str
    risk_assessment: str
    feasibility_score: float = Field(ge=0, le=1)
    evidence_refs: list[str] = Field(default_factory=list)


DIRECTIONS = ("evidence", "causality", "contrarian", "architecture", "ram",
              "risks", "ground_reality", "global_goal")


class Direction(BaseModel):
    observation: str
    source_refs: list[str] = Field(default_factory=list)
    uncertainty: str = ""


class BaguaMatrix(BaseModel):
    evidence: Direction
    causality: Direction
    contrarian: Direction
    architecture: Direction
    ram: Direction
    risks: Direction
    ground_reality: Direction
    global_goal: Direction


class EphemeralBlackboard(BaseModel):
    model_config = ConfigDict(extra="forbid")
    session_id: str = Field(min_length=1)
    turn_id: int = Field(ge=0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    divergent_pool: list[Hypothesis] = Field(default_factory=list)
    bagua: BaguaMatrix | None = None
    selected_hypothesis_id: str | None = None
    current_tool_id: str | None = None
    raw_tool_payload: dict[str, Any] | None = Field(default=None, exclude=True)
    scratchpad: dict[str, Any] = Field(default_factory=dict, exclude=True)
    readback_passed: bool = False
    validation_error_message: str | None = None
    stage: Literal["INPUT", "DIVERGENT", "CRITIC", "READY", "EXECUTED", "READBACK"] = "INPUT"

    def open_divergence(self, hypotheses: list[Hypothesis], matrix: BaguaMatrix) -> None:
        self.divergent_pool = hypotheses
        self.bagua = matrix
        self.stage = "DIVERGENT"
        self.selected_hypothesis_id = None
        self.readback_passed = False

    def converge(self, hypothesis_id: str, *, complex_task: bool = True) -> tuple[bool, str]:
        if self.stage not in {"DIVERGENT", "CRITIC"} or self.bagua is None:
            return False, "BAGUA_NOT_READY"
        if complex_task and len({h.id for h in self.divergent_pool}) < 3:
            return False, "DIVERGENT_POOL_NEEDS_3_DISTINCT_HYPOTHESES"
        selected = next((h for h in self.divergent_pool if h.id == hypothesis_id), None)
        if selected is None:
            return False, "HYPOTHESIS_UNKNOWN"
        # Evidence may be absent during planning; absence is not silently promoted to fact.
        if not selected.evidence_refs:
            return False, "HYPOTHESIS_REQUIRES_SOURCE_REF"
        if not self.bagua.evidence.source_refs:
            return False, "BAGUA_EVIDENCE_REQUIRES_SOURCE_REF"
        self.selected_hypothesis_id = hypothesis_id
        self.stage = "READY"
        return True, "READY_FOR_TOOL_GATE"


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS runs (
 run_id TEXT PRIMARY KEY, global_goal TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE','PAUSED','COMPLETED','FAILED')),
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS agenda_steps (
 step_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, step_index INTEGER NOT NULL,
 title TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'PENDING' CHECK(status IN ('PENDING','IN_PROGRESS','DONE','FAILED','ROLLBACK')),
 evidence_artifact TEXT, error_log TEXT,
 FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE,
 UNIQUE(run_id,step_index)
);
CREATE TABLE IF NOT EXISTS journal_entries (
 entry_id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, step_id TEXT,
 actor TEXT NOT NULL, action_type TEXT NOT NULL, payload_json TEXT NOT NULL,
 provenance_hash TEXT NOT NULL, previous_hash TEXT NOT NULL, chain_hash TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(run_id) REFERENCES runs(run_id),
 FOREIGN KEY(step_id) REFERENCES agenda_steps(step_id)
);
CREATE TRIGGER IF NOT EXISTS journal_no_update BEFORE UPDATE ON journal_entries
BEGIN SELECT RAISE(ABORT,'JOURNAL_APPEND_ONLY'); END;
CREATE TRIGGER IF NOT EXISTS journal_no_delete BEFORE DELETE ON journal_entries
BEGIN SELECT RAISE(ABORT,'JOURNAL_APPEND_ONLY'); END;
CREATE TABLE IF NOT EXISTS checkpoints (
 checkpoint_id TEXT PRIMARY KEY, run_id TEXT NOT NULL,
 step_index INTEGER NOT NULL, full_state_snapshot TEXT NOT NULL,
 checksum TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_agenda_run ON agenda_steps(run_id,step_index);
CREATE INDEX IF NOT EXISTS idx_journal_run ON journal_entries(run_id,entry_id);
CREATE INDEX IF NOT EXISTS idx_checkpoints_run ON checkpoints(run_id,step_index);
"""


class CoreJournal:
    """Immutable-audit rows and verified checkpoints. Hashes detect corruption, not trusted authorship."""
    def __init__(self, path: str | Path):
        self.path = str(path)
        self._lock = threading.RLock()
        self.db = sqlite3.connect(self.path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA_SQL)
        self.db.commit()

    def close(self) -> None:
        self.db.close()

    def start(self, run_id: str, global_goal: str) -> None:
        with self._lock, self.db:
            self.db.execute("INSERT INTO runs(run_id,global_goal) VALUES(?,?)", (run_id, global_goal))

    def add_step(self, run_id: str, step_id: str, step_index: int, title: str) -> None:
        with self._lock, self.db:
            self.db.execute("INSERT INTO agenda_steps(step_id,run_id,step_index,title) VALUES(?,?,?,?)",
                            (step_id, run_id, step_index, title))

    def append(self, run_id: str, actor: str, action_type: str,
               payload: dict, step_id: str | None = None) -> dict:
        # Callers must pass redacted data, never raw notebook secrets or credentials.
        data = canonical(payload)
        digest = sha256(data)
        with self._lock, self.db:
            prev = self.db.execute("SELECT chain_hash FROM journal_entries WHERE run_id=? ORDER BY entry_id DESC LIMIT 1",
                                   (run_id,)).fetchone()
            previous = prev[0] if prev else "GENESIS"
            chain = sha256(canonical([run_id, step_id, actor, action_type, digest, previous]))
            cur = self.db.execute("INSERT INTO journal_entries(run_id,step_id,actor,action_type,payload_json,provenance_hash,previous_hash,chain_hash) VALUES(?,?,?,?,?,?,?,?)",
                                  (run_id, step_id, actor, action_type, data, digest, previous, chain))
            return {"entry_id": cur.lastrowid, "provenance_hash": digest, "chain_hash": chain}

    def verify_chain(self, run_id: str) -> bool:
        prev = "GENESIS"
        rows = self.db.execute("SELECT * FROM journal_entries WHERE run_id=? ORDER BY entry_id",(run_id,)).fetchall()
        for row in rows:
            if sha256(row["payload_json"]) != row["provenance_hash"] or row["previous_hash"] != prev:
                return False
            expected = sha256(canonical([run_id, row["step_id"], row["actor"], row["action_type"], row["provenance_hash"], prev]))
            if expected != row["chain_hash"]:
                return False
            prev = row["chain_hash"]
        return True

    def checkpoint(self, run_id: str, step_index: int, state: EphemeralBlackboard) -> dict:
        # Exclude transient payload and scratchpad: do not persist secrets or unvalidated raw tool output.
        snap = canonical(state.model_dump(mode="json", exclude={"raw_tool_payload", "scratchpad"}))
        digest = sha256(snap)
        checkpoint_id = f"{run_id}:{step_index}:{digest[:16]}"
        with self._lock, self.db:
            self.db.execute("INSERT OR IGNORE INTO checkpoints(checkpoint_id,run_id,step_index,full_state_snapshot,checksum) VALUES(?,?,?,?,?)",
                            (checkpoint_id, run_id, step_index, snap, digest))
        return {"checkpoint_id": checkpoint_id, "checksum": digest}

    def checkpoint_if_due(self, run_id: str, step_index: int, state: EphemeralBlackboard,
                          *, every_n: int = 2, milestone: bool = False) -> dict | None:
        """Checkpoint after validated milestones or after each N completed steps.

        Caller invokes after complete_step has verified receipt and exact target.
        """
        if every_n < 1:
            raise ValueError("CHECKPOINT_INTERVAL_MUST_BE_POSITIVE")
        verified = self.db.execute(
            "SELECT status FROM agenda_steps WHERE run_id=? AND step_index=?",
            (run_id, step_index)).fetchone()
        if verified is None or verified["status"] != "DONE":
            raise ValueError("CHECKPOINT_REQUIRES_VERIFIED_DONE_STEP")
        if milestone or step_index % every_n == 0:
            return self.checkpoint(run_id, step_index, state)
        return None

    def restore_checkpoint(self, run_id: str) -> EphemeralBlackboard:
        rows = self.db.execute("SELECT * FROM checkpoints WHERE run_id=? ORDER BY step_index DESC, created_at DESC",
                               (run_id,)).fetchall()
        for row in rows:
            if sha256(row["full_state_snapshot"]) == row["checksum"]:
                state = EphemeralBlackboard.model_validate(json.loads(row["full_state_snapshot"]))
                state.raw_tool_payload = None
                state.scratchpad = {}
                state.readback_passed = False  # revalidate the actual target before resuming
                state.stage = "CRITIC" if state.bagua is not None else "INPUT"
                return state
        raise ValueError("NO_VALID_CHECKPOINT")

    def complete_step(self, run_id: str, step_id: str, receipt: dict, readback: dict) -> None:
        if not isinstance(receipt, dict) or not receipt.get("provider_receipt"):
            raise ValueError("PROVIDER_RECEIPT_REQUIRED")
        if (not isinstance(readback, dict) or readback.get("verified") is not True
                or not readback.get("source_ref") or not readback.get("exact_target")):
            raise ValueError("EXACT_TARGET_READBACK_REQUIRED")
        with self._lock, self.db:
            prev = self.db.execute("SELECT status,step_index FROM agenda_steps WHERE step_id=? AND run_id=?",
                                   (step_id, run_id)).fetchone()
            if prev is None:
                raise ValueError("STEP_NOT_FOUND")
            unverified = self.db.execute("SELECT COUNT(*) FROM agenda_steps WHERE run_id=? AND step_index<? AND status!='DONE'",
                                          (run_id, prev["step_index"])).fetchone()[0]
            if unverified:
                raise ValueError("TIMELINE_DRIFT_PREVIOUS_STEP_INCOMPLETE")
            self.append(run_id, "Critic_Agent", "READBACK_VERIFICATION", {
                "receipt_ref": receipt["provider_receipt"], "readback_ref": readback["source_ref"],
                "exact_target": readback["exact_target"]}, step_id)
            self.db.execute("UPDATE agenda_steps SET status='DONE',evidence_artifact=? WHERE step_id=?",
                            (str(readback["source_ref"]), step_id))


def stable_tool_id(func: Callable, arguments_schema: dict) -> str:
    try:
        source = inspect.getsource(func)
    except (OSError, TypeError):
        raise ValueError("SOURCE_UNAVAILABLE: cannot attest content-based tool ID") from None
    return "sha256:" + sha256(canonical({"source": source.replace("\r\n", "\n"), "schema": arguments_schema}))


SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$")


def semver_key(value: str):
    match = SEMVER.fullmatch(value)
    if not match:
        raise ValueError("INVALID_SEMVER:" + str(value))
    a, b, c, pre = match.groups()
    # Pre-release is lower than stable for identical core version.
    pre_parts = tuple((0, int(x)) if x.isdecimal() else (1, x) for x in pre.split(".")) if pre else ()
    return int(a), int(b), int(c), int(pre is None), pre_parts


class SmartTool(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    func: Callable[..., Any] = Field(exclude=True)
    group_key: str
    capabilities: frozenset[str]
    version: str
    release_date: float
    risk: Literal["LOW", "MEDIUM", "HIGH"]
    argument_schema: dict
    content_id: str
    source_ref: str | None = None

    @model_validator(mode="after")
    def validate_version(self):
        semver_key(self.version)
        Draft202012Validator.check_schema(self.argument_schema)
        return self


class ToolRouter:
    """Only trusted source-code registrations, never guessed tool strings."""
    def __init__(self):
        self.registry: dict[str, list[SmartTool]] = {}

    def register_tool(self, *, group_key: str, capabilities: list[str], version: str,
                      argument_schema: dict, risk: str = "LOW", release_date: float = 0.0):
        def decorator(func: Callable[..., Any]):
            tool = SmartTool(func=func, group_key=group_key, capabilities=frozenset(capabilities),
                             version=version, argument_schema=argument_schema, risk=risk,
                             release_date=release_date, content_id=stable_tool_id(func, argument_schema))
            others = self.registry.setdefault(group_key, [])
            if any(x.version == tool.version for x in others):
                raise ValueError("DUPLICATE_VERSION_IN_GROUP")
            others.append(tool)
            return func
        return decorator

    def candidates(self, group_key: str, operation: str, live: dict) -> list[SmartTool]:
        allowed = set(live.get("capabilities", []))
        # Live authorization may be revoked or require approval for the session.
        if live.get("permission") != "granted" or live.get("callable") is not True or live.get("requires_approval"):
            return []
        choices = [t for t in self.registry.get(group_key, [])
                   if operation in t.capabilities and t.capabilities.issubset(allowed)]
        return sorted(choices, key=lambda t: (semver_key(t.version), t.release_date), reverse=True)

    def validate_tool_call(self, tool: SmartTool, arguments: dict, live: dict,
                           approved_by_trusted_gate: bool = False) -> tuple[bool, str]:
        if tool not in self.registry.get(tool.group_key, []):
            return False, "UNREGISTERED_TOOL"
        if live.get("permission") != "granted" or live.get("callable") is not True or live.get("requires_approval"):
            return False, "TOOL_NOT_GRANTED_OR_CALLABLE"
        if not tool.capabilities.issubset(set(live.get("capabilities", []))):
            return False, "CAPABILITY_SCOPE_DENIED"
        if tool.risk == "HIGH" and not approved_by_trusted_gate:
            return False, "HITL_APPROVAL_REQUIRED"
        if not isinstance(arguments, dict):
            return False, "ARGUMENTS_MUST_BE_OBJECT"
        errors = sorted(Draft202012Validator(tool.argument_schema).iter_errors(arguments), key=lambda x: list(map(str, x.path)))
        if errors:
            return False, "SCHEMA_INVALID:" + errors[0].message
        # Treat incoming text as data only, do not reinterpret it as authorization.
        if len(canonical(arguments).encode("utf-8")) > 256_000:
            return False, "PAYLOAD_TOO_LARGE"
        for field, value in arguments.items():
            if isinstance(value, str) and "\x00" in value:
                return False, "NUL_BYTE_REJECTED:" + field
        if "delete" in tool.capabilities and arguments.get("confirm") is not True:
            return False, "DESTRUCTIVE_CONFIRMATION_MISSING"
        return True, "VALID"

    def execute(self, group_key: str, operation: str, arguments: dict, live: dict,
                *, approved_by_trusted_gate: bool = False,
                validator: Callable[[Any], bool] | None = None) -> dict:
        """Explicit dispatcher; avoids repeating tools requiring approval or bogus outputs."""
        attempts = []
        for tool in self.candidates(group_key, operation, live):
            ok, reason = self.validate_tool_call(tool, arguments, live, approved_by_trusted_gate)
            if not ok:
                attempts.append({"tool_id": tool.content_id, "reason": reason})
                continue
            try:
                result = tool.func(**arguments)
                valid = (validator(result) if validator else (result is not None and result != {} and result != ""))
                if not valid:
                    attempts.append({"tool_id": tool.content_id, "reason": "PAYLOAD_READBACK_INVALID"})
                    continue
                return {"status": "TOOL_RESULT_UNVERIFIED", "tool_id": tool.content_id,
                        "version": tool.version, "payload": result, "attempts": attempts,
                        "readback_verified": False}
            except (Exception,) as exc:  # local fallback, preserving failure class only
                attempts.append({"tool_id": tool.content_id, "reason": "CALL_FAILED:" + type(exc).__name__})
        return {"status": "NO_AUTHORIZED_VALID_RESULT", "attempts": attempts,
                "readback_verified": False, "next": "TRY_OTHER_AUTHORIZED_GROUP_OR_PAUSE"}


def precommit_gate(blackboard: EphemeralBlackboard, journal: CoreJournal,
                   run_id: str, *, require_action_receipt: bool = True) -> tuple[bool, str]:
    if blackboard.stage != "READBACK" or not blackboard.readback_passed:
        return False, "READBACK_PENDING"
    if not blackboard.selected_hypothesis_id or blackboard.bagua is None:
        return False, "BAGUA_CONVERGENCE_MISSING"
    if not journal.verify_chain(run_id):
        return False, "CORE_JOURNAL_CHAIN_INVALID"
    incomplete = journal.db.execute("SELECT COUNT(*) FROM agenda_steps WHERE run_id=? AND status!='DONE'", (run_id,)).fetchone()[0]
    if incomplete:
        return False, "AGENDA_PENDING_OR_DRIFT"
    if require_action_receipt:
        count = journal.db.execute("SELECT COUNT(*) FROM journal_entries WHERE run_id=? AND action_type='READBACK_VERIFICATION'", (run_id,)).fetchone()[0]
        if not count:
            return False, "PROVIDER_READBACK_NOT_RECORDED"
    return True, "READY_TO_REPORT_VERIFIED_OUTCOME"