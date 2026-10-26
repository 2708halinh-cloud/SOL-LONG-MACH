#!/usr/bin/env python3
"""GGDV TESSERACT 6D: X2 Âm/Dương -> provenance -> Hebbian activation.

Reads an SQLite event carrier in read-only mode; never reads hidden RAM,
modifies the source, mounts VHDX, or manufactures events. Derived weights are
transactional and idempotent. Ingest requires a trusted authorization verifier
injected by an authorized caller; the CLI intentionally exposes no ingest action
until that verifier is wired. A non-empty origin string is not authorization.
Existing UBUBU API/journals remain authoritative.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from collections.abc import Callable, Mapping

try:
    from .motherboard_control_plane import gate1_preflight, gate2_readback
except ImportError:  # direct script execution from runtime/ directory
    from motherboard_control_plane import gate1_preflight, gate2_readback

DEFAULT_SOURCE = Path(r"D:\UBUBU\sqlite\ububu_memory.sqlite3")
DEFAULT_ROOT = Path(r"G:\OS_Workspace\TESSERACT_OS")
DB_REL = Path("03_Synapse_Z") / "synapses_6d.sqlite3"
AXES = ("01_Physical_X", "02_Journal_Y", "03_Synapse_Z", "04_Timeline_T", "05_Will_U", "06_Parallel_V")
MAX_FEATURES_PER_EVENT = 24
HEBB_DELTA = 0.10
MAX_WEIGHT = 10.0
FEATURE_REGEX = re.compile(r"[^\W_][\w-]{1,50}", re.UNICODE)
STOP_WORDS = frozenset(("và", "là", "của", "trong", "được", "cho", "với", "những", "này", "các", "một", "the", "from", "that", "with"))

class GateRejected(RuntimeError):
    pass


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def connect_readonly(source: Path) -> sqlite3.Connection:
    if not source.is_file():
        raise GateRejected("GATE1: source carrier absent; search authorized carriers")
    uri = source.resolve().as_uri() + "?mode=ro"
    c = sqlite3.connect(uri, uri=True)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA query_only=ON")
    return c


def discover_source(c: sqlite3.Connection) -> dict:
    tables = {x[0] for x in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "memories" not in tables:
        return {"tables": sorted(tables), "compatible": False, "reason": "no UBUBU memories table; do not guess Meta.db mapping"}
    cols = {r[1] for r in c.execute("PRAGMA table_info(memories)")}
    required = {"event_id", "content", "created_at"}
    return {"tables": sorted(tables), "columns": sorted(cols), "compatible": required <= cols,
            "count": c.execute("SELECT COUNT(*) FROM memories").fetchone()[0]}


def connect_graph(root: Path) -> sqlite3.Connection:
    root.mkdir(parents=True, exist_ok=True)
    for axis in AXES:
        (root / axis).mkdir(exist_ok=True)
    dbpath = root / DB_REL
    c = sqlite3.connect(dbpath)
    c.execute("PRAGMA foreign_keys=ON")
    c.execute("PRAGMA journal_mode=WAL")
    c.executescript("""
    CREATE TABLE IF NOT EXISTS neurons (
      id TEXT PRIMARY KEY, cue TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL,
      firing_count INTEGER NOT NULL DEFAULT 0, last_activated TEXT,
      source_anchor_count INTEGER NOT NULL DEFAULT 0);
    CREATE TABLE IF NOT EXISTS synapses (
      a TEXT NOT NULL, b TEXT NOT NULL, weight REAL NOT NULL,
      coactivation_count INTEGER NOT NULL DEFAULT 0, last_activated TEXT NOT NULL,
      PRIMARY KEY(a,b), FOREIGN KEY(a) REFERENCES neurons(id),
      FOREIGN KEY(b) REFERENCES neurons(id), CHECK(a < b));
    CREATE TABLE IF NOT EXISTS source_anchors (
      event_id TEXT PRIMARY KEY, row_sha256 TEXT NOT NULL, provenance TEXT NOT NULL,
      fired_at TEXT NOT NULL, x TEXT NOT NULL, y TEXT NOT NULL,
      t TEXT NOT NULL, u TEXT NOT NULL, v TEXT NOT NULL,
      x2_yin INTEGER NOT NULL CHECK(x2_yin=1),
      x2_yang INTEGER NOT NULL CHECK(x2_yang=1));
    CREATE INDEX IF NOT EXISTS idx_synapse_weight ON synapses(weight DESC);
    CREATE TABLE IF NOT EXISTS neuron_anchors (
      neuron_id TEXT NOT NULL, event_id TEXT NOT NULL,
      PRIMARY KEY(neuron_id,event_id),
      FOREIGN KEY(neuron_id) REFERENCES neurons(id),
      FOREIGN KEY(event_id) REFERENCES source_anchors(event_id));
    CREATE INDEX IF NOT EXISTS idx_neuron_anchors_event ON neuron_anchors(event_id);
    """)
    return c


def tokenize(row: dict) -> list[str]:
    # A memory is not copied to the graph. Only cues and stable coactivation links.
    fields = (row.get("cue"), row.get("objective_id"), row.get("memory_type"), row.get("wave"),
              row.get("tags"), row.get("consequence"), row.get("content"))
    seen = set()
    selected = []
    for txt in fields:
        if not txt:
            continue
        for word in FEATURE_REGEX.findall(str(txt).casefold()):
            if word in STOP_WORDS or word in seen or len(word) < 2:
                continue
            seen.add(word)
            selected.append(word)
            if len(selected) >= MAX_FEATURES_PER_EVENT:
                return selected
    return selected


def activate(
    c: sqlite3.Connection, row: dict, source: Path, origin: str, will: str, branch: str,
    *, gate1_context: Mapping[str, bool] | None = None,
    expected_target: Path | None = None,
) -> str:
    # Gate 1: source/causality and X2 polarities, no premature action.
    eid = str(row.get("event_id") or "").strip()
    created = str(row.get("created_at") or "").strip()
    if not eid or not created or not row.get("content") or not origin or not will or not branch:
        raise GateRejected("GATE1: required provenance, timestamp, objective, or source missing")
    db_identity = c.execute("PRAGMA database_list").fetchone()[2]
    actual_target = Path(db_identity).resolve() if db_identity else None
    expected_target_resolved = expected_target.resolve() if expected_target is not None else None
    target_matches = bool(
        gate1_context
        and gate1_context.get("target_identity_verified") is True
        and actual_target is not None
        and expected_target_resolved is not None
        and actual_target == expected_target_resolved
        and actual_target.is_file()
        and source.is_file()
    )
    preflight = gate1_preflight(
        authorized=bool(gate1_context and gate1_context.get("authorized") is True),
        target_identity_verified=target_matches,
        policy_allowed=bool(gate1_context and gate1_context.get("policy_allowed") is True),
        quota_available=bool(gate1_context and gate1_context.get("quota_available") is True),
    )
    if not preflight.allowed:
        raise GateRejected("GATE1: " + ",".join(preflight.reasons))
    row_hash = digest(json.dumps(row, sort_keys=True, ensure_ascii=False, default=str, separators=(",", ":")))
    existing = c.execute("SELECT row_sha256 FROM source_anchors WHERE event_id=?", (eid,)).fetchone()
    if existing:
        if existing[0] != row_hash:
            raise GateRejected("GATE1: historical event ID collision; STOP and backtrace")
        return "REUSED"  # no fake replay, no additional Hebbian increment
    features = tokenize(row)
    if not features:
        raise GateRejected("GATE1: no authentic activation cues")
    now = datetime.now(timezone.utc).isoformat()
    ids = sorted({digest("CUE:" + f) for f in features})
    by_id = {digest("CUE:" + f): f for f in features}
    # Gate 2 is coupled to this SQL transaction and exact-target readback.
    with c:
        for nid in ids:
            c.execute("INSERT OR IGNORE INTO neurons(id,cue,created_at) VALUES(?,?,?)", (nid,by_id[nid],now))
            c.execute("UPDATE neurons SET firing_count=firing_count+1,source_anchor_count=source_anchor_count+1,last_activated=? WHERE id=?", (now,nid))
        for a,b in itertools.combinations(ids,2):
            c.execute("""INSERT INTO synapses(a,b,weight,coactivation_count,last_activated)
              VALUES(?,?,?,1,?) ON CONFLICT(a,b) DO UPDATE SET
              weight=MIN(?,synapses.weight+?),coactivation_count=synapses.coactivation_count+1,
              last_activated=excluded.last_activated""", (a,b,HEBB_DELTA,now,MAX_WEIGHT,HEBB_DELTA))
        c.execute("""INSERT INTO source_anchors(event_id,row_sha256,provenance,fired_at,x,y,t,u,v,x2_yin,x2_yang)
                     VALUES(?,?,?,?,?,?,?,?,?,1,1)""",
                  (eid,row_hash,origin+"|"+str(source),now,str(source),row.get("source_refs") or "[]",created,will,branch))
        for nid in ids:
            c.execute("INSERT INTO neuron_anchors(neuron_id,event_id) VALUES(?,?)",(nid,eid))
        reread = c.execute("SELECT row_sha256,x2_yin,x2_yang FROM source_anchors WHERE event_id=?", (eid,)).fetchone()
        if reread is None or tuple(reread) != (row_hash,1,1):
            raise GateRejected("GATE2: exact-target readback inconsistent")
    # Gate 2: commit is followed by a fresh read through a separate read-only connection.
    db_path = Path(c.execute("PRAGMA database_list").fetchone()[2])
    if not db_path.is_file():
        raise GateRejected("GATE2: database carrier path unavailable for independent readback")
    verify_uri = db_path.resolve().as_uri() + "?mode=ro"
    verify = sqlite3.connect(verify_uri, uri=True)
    try:
        verify.execute("PRAGMA query_only=ON")
        independent = verify.execute(
            "SELECT row_sha256,x2_yin,x2_yang FROM source_anchors WHERE event_id=?", (eid,)
        ).fetchone()
    finally:
        verify.close()
    consistent = independent is not None and tuple(independent) == (row_hash, 1, 1)
    gate2 = gate2_readback(
        action_receipt=reread is not None,
        consequence_observed=True,
        independent_readback=independent is not None,
        state_consistent=consistent,
    )
    if not gate2.allowed:
        raise GateRejected("GATE2: " + ",".join(gate2.reasons))
    return "ACTIVATED"


def recall_network(root: Path, cue: str, limit: int = 12) -> dict:
    """Read existing synaptic graph, return weighted relationships and source event IDs.

    Original content stays in UBUBU and is fetched via its authorized API on demand.
    """
    target = root / DB_REL
    if not target.is_file():
        raise GateRejected("Graph carrier absent: reentry must probe first")
    c = sqlite3.connect(target.resolve().as_uri()+"?mode=ro",uri=True)
    c.row_factory = sqlite3.Row
    try:
        seeds = [digest("CUE:" + x) for x in FEATURE_REGEX.findall(cue.casefold()) if len(x)>1]
        if not seeds:
            return {"cue":cue,"linked_events":[],"associated_cues":[]}
        placeholders=",".join("?" for _ in seeds)
        query=f"""SELECT n.cue, s.weight, s.coactivation_count, n.id
                    FROM synapses s JOIN neurons n ON n.id=CASE WHEN s.a IN ({placeholders}) THEN s.b ELSE s.a END
                    WHERE s.a IN ({placeholders}) OR s.b IN ({placeholders})
                    ORDER BY s.weight DESC,s.coactivation_count DESC LIMIT ?"""
        rows=[dict(r) for r in c.execute(query, (*seeds,*seeds,*seeds,limit))]
        involved=list(dict.fromkeys(seeds + [r['id'] for r in rows]))
        refs=[]
        if involved:
            ref_marks=','.join('?' for _ in involved)
            refs=[r[0] for r in c.execute(f"SELECT DISTINCT event_id FROM neuron_anchors WHERE neuron_id IN ({ref_marks}) ORDER BY event_id LIMIT ?", (*involved,limit))]
        return {"cue":cue,"associated_cues":[{k:x[k] for k in ('cue','weight','coactivation_count')} for x in rows],"linked_events":refs,"source":"UBUBU original records; no copied content"}
    finally:
        c.close()


def rows_from_source(c: sqlite3.Connection, max_rows: int):
    available = {r[1] for r in c.execute("PRAGMA table_info(memories)")}
    selected = [k for k in ("event_id","created_at","cue","objective_id","memory_type","wave","tags","consequence","content","source_refs") if k in available]
    sql = "SELECT " + ",".join('"'+x+'"' for x in selected) + " FROM memories ORDER BY rowid ASC LIMIT ?"
    for r in c.execute(sql, (max_rows,)):
        yield dict(r)


def run(
    source: Path, root: Path, action: str, max_rows: int, will: str, branch: str, *,
    authorization_verifier: Callable[..., Mapping[str, bool]] | None = None,
) -> dict:
    source_c = connect_readonly(source)
    try:
        d = discover_source(source_c)
        if action == "probe":
            return {"action":"probe","source":str(source),"source_schema":d,"axes":AXES,"x2":"YIN_SOURCE_AND_CONSEQUENCE + YANG_GATED_ACTION"}
        if action not in {"dry-run", "ingest"}:
            raise GateRejected("GATE1: unsupported run action; recall uses recall_network")
        if not d["compatible"]:
            raise GateRejected("GATE1: unsupported source schema; use provider-specific adapter")
        if action == "dry-run":
            samples = list(rows_from_source(source_c, max_rows))
            return {"action":"dry-run","candidate_events":len(samples),"eligible":sum(bool(tokenize(row)) for row in samples),"mutated":False}
        gate1_context = None
        expected_target = None
        if action == "ingest":
            if authorization_verifier is None:
                raise GateRejected("GATE1: trusted authorization verifier not configured; ingest disabled")
            source_identity = source.resolve(strict=True)
            root_identity = root.resolve()
            expected_target = (root_identity / DB_REL).resolve()
            try:
                expected_target.relative_to(root_identity)
            except ValueError as exc:
                raise GateRejected("GATE1: graph target resolves outside the authorized root") from exc
            gate1_context = authorization_verifier(
                action="ingest",
                source=source_identity,
                target=expected_target,
                will=will,
                branch=branch,
            )
            if not isinstance(gate1_context, Mapping):
                raise GateRejected("GATE1: authorization verifier returned no structured decision")
            preflight = gate1_preflight(
                authorized=gate1_context.get("authorized") is True,
                target_identity_verified=(
                    gate1_context.get("target_identity_verified") is True
                    and expected_target.is_relative_to(root_identity)
                ),
                policy_allowed=gate1_context.get("policy_allowed") is True,
                quota_available=gate1_context.get("quota_available") is True,
            )
            if not preflight.allowed:
                raise GateRejected("GATE1: " + ",".join(preflight.reasons))
        graph = connect_graph(root)
        try:
            new = old = 0
            for row in rows_from_source(source_c, max_rows):
                result = activate(
                    graph, row, source, "UBUBU_SQLITE_READONLY", will, branch,
                    gate1_context=gate1_context, expected_target=expected_target,
                )
                new += result == "ACTIVATED"
                old += result == "REUSED"
            neurons,edges,anchors=(graph.execute("SELECT COUNT(*) FROM "+table).fetchone()[0] for table in ("neurons","synapses","source_anchors"))
            return {"action":"ingest","new_activations":new,"reused":old,"neurons":neurons,"synapses":edges,"source_anchors":anchors,"graph":str(root/DB_REL),"x2":"BOTH_POLARITIES_APPLIED","readback":"PASS"}
        finally:
            graph.close()
    finally:
        source_c.close()


def main():
    ap=argparse.ArgumentParser(description="GGDV TESSERACT 6D Hebbian transducer")
    ap.add_argument("action",choices=["probe","dry-run","recall"], help="ingest is disabled in the CLI until a trusted authorization verifier is wired")
    ap.add_argument("--source",type=Path,default=DEFAULT_SOURCE)
    ap.add_argument("--root",type=Path,default=DEFAULT_ROOT)
    ap.add_argument("--limit",type=int,default=500)
    ap.add_argument("--cue",default="")
    ap.add_argument("--will",default="HA_LINH_SOURCE_DIRECT")
    ap.add_argument("--branch",default="SOL_GGDV")
    args=ap.parse_args()
    if not 1 <= args.limit <= 10000:
        ap.error("limit must be 1..10000")
    try:
        result = recall_network(args.root,args.cue,args.limit) if args.action == "recall" else run(args.source,args.root,args.action,args.limit,args.will,args.branch)
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (GateRejected,sqlite3.DatabaseError,OSError) as e:
        raise SystemExit(str(e)) from e

if __name__ == "__main__":
    main()
