"""TESSERACT functional homeostatic drive and auditable policy plasticity scaffold.

Engineered control signals only; this module does not establish biological pain,
consciousness, or subjective experience. Standard library only.
"""
from __future__ import annotations
import argparse, hashlib, json, math, sqlite3, uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "TESSERACT_AFFECTIVE_HOMEOSTASIS/1.0"

def now():
    return datetime.now(timezone.utc).isoformat()

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, float(x)))

@dataclass(frozen=True)
class Telemetry:
    prediction_error: float = 0.0
    tool_failure_fraction: float = 0.0
    consecutive_failures: int = 0
    cpu_load: float | None = None
    ram_used_fraction: float | None = None
    disk_used_fraction: float | None = None
    token_budget_used_fraction: float | None = None
    gpu_temperature_c: float | None = None
    active_seconds: float = 0.0
    new_information_fraction: float = 0.0
    uncertainty_before: float = 0.0
    uncertainty_after: float = 0.0
    goal_progress: float = 0.0

    def validate(self):
        for k in ("prediction_error", "tool_failure_fraction", "new_information_fraction",
                  "uncertainty_before", "uncertainty_after", "goal_progress"):
            v = getattr(self, k)
            if not math.isfinite(v) or not 0 <= v <= 1:
                raise ValueError(f"{k} must be finite and in [0,1]")
        for k in ("cpu_load", "ram_used_fraction", "disk_used_fraction", "token_budget_used_fraction"):
            v = getattr(self, k)
            if v is not None and (not math.isfinite(v) or not 0 <= v <= 1):
                raise ValueError(f"{k} must be None or in [0,1]")
        if self.gpu_temperature_c is not None and not -20 <= self.gpu_temperature_c <= 150:
            raise ValueError("GPU temperature outside accepted sensor range")
        if self.consecutive_failures < 0 or self.active_seconds < 0:
            raise ValueError("negative failure count or active time")

def derive_state(t: Telemetry, previous_fatigue=0.0, disk_threshold=0.90, gpu_hot_c=83.0):
    t.validate()
    resources = [v for v in (t.cpu_load, t.ram_used_fraction, t.token_budget_used_fraction,
                             t.disk_used_fraction) if v is not None]
    if t.gpu_temperature_c is not None:
        resources.append(clamp((t.gpu_temperature_c - 45.0) / (gpu_hot_c - 45.0)))
    pressure = sum(resources) / len(resources) if resources else 0.0
    homeostatic_error = clamp(.35*t.prediction_error + .30*t.tool_failure_fraction +
                              .20*pressure + .15*clamp(t.consecutive_failures/5))
    stress = clamp(.65*homeostatic_error + .35*t.prediction_error)
    fatigue = clamp(.75*clamp(previous_fatigue) +
                    .15*clamp(t.active_seconds/3600) + .10*pressure)
    curiosity = clamp(.60*t.new_information_fraction +
                      .40*max(0, t.uncertainty_before-t.uncertainty_after))
    reward = clamp(.60*t.goal_progress + .40*curiosity)
    valence = clamp(.5 + .5*(reward-stress))*2 - 1
    arousal = clamp(.55*stress + .25*curiosity + .20*pressure)
    mode, reasons = "NORMAL", []
    if t.disk_used_fraction is not None and t.disk_used_fraction >= disk_threshold:
        mode, reasons = "DEFENSIVE", ["DISK_WATERMARK_REACHED"]
    elif stress >= .75 or t.consecutive_failures >= 3:
        mode, reasons = "STRESSED", ["PREDICTION_OR_TOOL_FAILURE_PRESSURE"]
    elif fatigue >= .70:
        mode, reasons = "FATIGUED", ["COMPUTE_FATIGUE_ACCUMULATED"]
    elif curiosity >= .55:
        mode, reasons = "CURIOUS", ["NOVELTY_OR_UNCERTAINTY_REDUCTION"]
    gain = clamp(1 - .55*stress - .35*fatigue, .15, 1)
    allow_sensitive_write = mode == "NORMAL" and stress < .50
    if not allow_sensitive_write:
        reasons.append("SENSITIVE_WRITES_REQUIRE_INDEPENDENT_REAUTHORIZATION")
    return dict(homeostatic_error=homeostatic_error, stress=stress, fatigue=fatigue,
                curiosity=curiosity, reward=reward, valence=valence, arousal=arousal,
                mode=mode, response_gain=gain,
                write_sensitive_data_allowed=allow_sensitive_write, reasons=reasons)

SCHEMA_SQL = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS affective_events(
 event_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, schema_version TEXT NOT NULL,
 source_ref TEXT NOT NULL, telemetry_json TEXT NOT NULL, state_json TEXT NOT NULL,
 previous_event_hash TEXT, event_hash TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS affective_state_current(
 singleton INTEGER PRIMARY KEY CHECK(singleton=1), event_id TEXT NOT NULL REFERENCES affective_events(event_id),
 state_json TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS plasticity_traces(
 trace_id TEXT PRIMARY KEY, created_at TEXT NOT NULL,
 source_event_id TEXT NOT NULL REFERENCES affective_events(event_id),
 policy_key TEXT NOT NULL, delta REAL NOT NULL CHECK(delta BETWEEN -0.10 AND 0.10),
 confidence REAL NOT NULL CHECK(confidence BETWEEN 0 AND 1), rationale TEXT NOT NULL,
 UNIQUE(source_event_id,policy_key));
CREATE TABLE IF NOT EXISTS novelty_receipts(
 receipt_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, carrier TEXT NOT NULL, locator TEXT NOT NULL,
 content_sha256 TEXT, novelty_score REAL NOT NULL CHECK(novelty_score BETWEEN 0 AND 1),
 indexed INTEGER NOT NULL CHECK(indexed IN (0,1)), source_ref TEXT NOT NULL,
 UNIQUE(carrier,locator,content_sha256));
CREATE TRIGGER IF NOT EXISTS affective_events_no_update BEFORE UPDATE ON affective_events
 BEGIN SELECT RAISE(ABORT,'AFFECTIVE_EVENTS_APPEND_ONLY'); END;
CREATE TRIGGER IF NOT EXISTS affective_events_no_delete BEFORE DELETE ON affective_events
 BEGIN SELECT RAISE(ABORT,'AFFECTIVE_EVENTS_APPEND_ONLY'); END;
CREATE TRIGGER IF NOT EXISTS plasticity_traces_no_update BEFORE UPDATE ON plasticity_traces
 BEGIN SELECT RAISE(ABORT,'PLASTICITY_TRACES_APPEND_ONLY'); END;
CREATE TRIGGER IF NOT EXISTS plasticity_traces_no_delete BEFORE DELETE ON plasticity_traces
 BEGIN SELECT RAISE(ABORT,'PLASTICITY_TRACES_APPEND_ONLY'); END;
"""

class AffectiveStore:
    """Additive SQLite schema; never drops or rewrites pre-existing tables."""
    def __init__(self, db_path):
        self.db_path = str(db_path)
    def connect(self):
        con = sqlite3.connect(self.db_path, timeout=10)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA busy_timeout=10000")
        return con
    def initialize(self):
        with self.connect() as con:
            con.executescript(SCHEMA_SQL)
    def record(self, telemetry: Telemetry, source_ref: str, previous_fatigue=0.0):
        if not source_ref.strip():
            raise ValueError("source_ref is required")
        telemetry.validate()
        event_id, created = str(uuid.uuid4()), now()
        telemetry_json = json.dumps(asdict(telemetry), sort_keys=True, separators=(",", ":"))
        state_json = json.dumps(derive_state(telemetry, previous_fatigue), sort_keys=True, separators=(",", ":"))
        with self.connect() as con:
            prev = con.execute("SELECT event_hash FROM affective_events ORDER BY rowid DESC LIMIT 1").fetchone()
            previous_hash = prev["event_hash"] if prev else None
            canonical = json.dumps(dict(event_id=event_id, created_at=created, schema_version=SCHEMA_VERSION,
                source_ref=source_ref, telemetry_json=telemetry_json, state_json=state_json,
                previous_event_hash=previous_hash), sort_keys=True, separators=(",", ":"))
            digest = hashlib.sha256(canonical.encode()).hexdigest()
            con.execute("INSERT INTO affective_events VALUES(?,?,?,?,?,?,?,?)",
                (event_id, created, SCHEMA_VERSION, source_ref, telemetry_json, state_json, previous_hash, digest))
            con.execute("""INSERT INTO affective_state_current VALUES(1,?,?,?)
                ON CONFLICT(singleton) DO UPDATE SET event_id=excluded.event_id,
                state_json=excluded.state_json,updated_at=excluded.updated_at""",
                (event_id, state_json, created))
        return dict(event_id=event_id, event_hash=digest, previous_event_hash=previous_hash,
                    state=json.loads(state_json), readback=self.read_current())
    def read_current(self):
        with self.connect() as con:
            r = con.execute("""SELECT c.event_id,c.state_json,c.updated_at,e.event_hash,e.source_ref
                FROM affective_state_current c JOIN affective_events e USING(event_id)
                WHERE c.singleton=1""").fetchone()
        return None if r is None else dict(event_id=r["event_id"], state=json.loads(r["state_json"]),
            updated_at=r["updated_at"], event_hash=r["event_hash"], source_ref=r["source_ref"])
    def record_novelty(self, carrier, locator, source_ref, content_sha256, novelty_score, indexed):
        rid = str(uuid.uuid4())
        with self.connect() as con:
            con.execute("""INSERT OR IGNORE INTO novelty_receipts VALUES(?,?,?,?,?,?,?,?)""",
                (rid, now(), carrier, locator, content_sha256, clamp(novelty_score), int(indexed), source_ref))
        return rid
    def imprint_trace(self, source_event_id, policy_key, delta, confidence, rationale):
        if not policy_key.strip() or not rationale.strip():
            raise ValueError("policy_key and rationale are required")
        trace_id = str(uuid.uuid4())
        with self.connect() as con:
            con.execute("INSERT INTO plasticity_traces VALUES(?,?,?,?,?,?,?)",
                (trace_id, now(), source_event_id, policy_key, max(-.10,min(.10,float(delta))),
                 clamp(confidence), rationale))
        return trace_id
    def effective_policy_bias(self, policy_key):
        with self.connect() as con:
            rows = con.execute("SELECT delta,confidence FROM plasticity_traces WHERE policy_key=?",
                               (policy_key,)).fetchall()
        return max(-1, min(1, sum(r["delta"]*r["confidence"] for r in rows)))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", required=True, help="explicit SQLite path; use a disposable database first")
    p.add_argument("--demo", action="store_true", help="record synthetic telemetry only")
    a = p.parse_args()
    store = AffectiveStore(a.db)
    store.initialize()
    if a.demo:
        result = store.record(Telemetry(prediction_error=.8, tool_failure_fraction=.6,
            consecutive_failures=2, cpu_load=.7, ram_used_fraction=.8,
            disk_used_fraction=.4, active_seconds=1800, new_information_fraction=.2),
            "demo://synthetic-telemetry")
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(dict(schema=SCHEMA_VERSION, database=str(Path(a.db).resolve()),
                              initialized=True, current_state=store.read_current()), indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
