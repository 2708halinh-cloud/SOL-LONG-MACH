"""Local-first durable workrooms for Dương (human) and Âm (AI agents)."""
from __future__ import annotations

import json
import re
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

MAX_TEXT = 12000
VALID_KINDS = {"message", "task", "source", "feedback", "plan", "result", "receipt", "assignment"}
ROLES = {"DUONG_PHAP_SU", "AM_PHAP_SU", "SPECIALIST_AGENT"}
AGENTS = {
    "sol": {"label": "ÂM PHÁP SƯ / SOL", "skills": ["orchestration", "source_trace"]},
    "researcher": {"label": "Research Agent", "skills": ["source_search"]},
    "analyst": {"label": "Language Agent", "skills": ["entities", "sentiment"]},
    "router": {"label": "Power Router Agent", "skills": ["tool_discovery"]},
    "translator": {"label": "Translation Agent", "skills": ["translation_basic"]},
    "vision": {"label": "Vision Agent", "skills": ["faces", "landmarks", "logos"]},
    "transcriber": {"label": "Speech Agent", "skills": ["transcription"]},
    "video": {"label": "Video Agent", "skills": ["video_objects", "video_actions"]},
}

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def clean_text(value: object, field: str, limit: int = MAX_TEXT) -> str:
    if not isinstance(value, str):
        raise ValueError(field + "_MUST_BE_TEXT")
    text = value.strip()
    if not text or len(text) > limit:
        raise ValueError(field + "_MUST_BE_NONEMPTY_AND_BOUNDED")
    return text

class Workrooms:
    def __init__(self, db: Path):
        self.db = Path(db).expanduser().resolve()
        self.db.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        with self._connect() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS rooms (
                id TEXT PRIMARY KEY, title TEXT NOT NULL, created_at TEXT NOT NULL
            )""")
            c.execute("""CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY, room_id TEXT NOT NULL, actor TEXT NOT NULL,
                role TEXT NOT NULL, kind TEXT NOT NULL, content TEXT NOT NULL,
                source_ref TEXT, metadata TEXT NOT NULL, created_at TEXT NOT NULL,
                FOREIGN KEY(room_id) REFERENCES rooms(id)
            )""")
            c.execute("CREATE INDEX IF NOT EXISTS idx_events_room ON events(room_id,created_at)")
            c.execute("INSERT OR IGNORE INTO rooms(id,title,created_at) VALUES(?,?,?)",
                      ("sol-main", "SOL — ÂM–DƯƠNG PHÁP SƯ", utc_now()))

    def _connect(self):
        c = sqlite3.connect(str(self.db), timeout=10)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA busy_timeout = 10000")
        c.execute("PRAGMA foreign_keys = ON")
        return c

    def rooms(self):
        with self.lock, self._connect() as c:
            return [dict(r) for r in c.execute("SELECT * FROM rooms ORDER BY created_at,id")]

    def add_room(self, title: str):
        title = clean_text(title, "TITLE", 120)
        room = "room_" + uuid.uuid4().hex[:16]
        with self.lock, self._connect() as c:
            c.execute("INSERT INTO rooms VALUES(?,?,?)", (room, title, utc_now()))
        return room

    def add(self, room_id: str, actor: str, role: str, kind: str,
            content: str, *, source_ref: str | None = None, metadata: dict | None = None):
        if role not in ROLES or kind not in VALID_KINDS:
            raise ValueError("INVALID_ROLE_OR_EVENT_KIND")
        actor = clean_text(actor, "ACTOR", 80)
        content = clean_text(content, "CONTENT")
        if not isinstance(room_id, str) or len(room_id) > 100:
            raise ValueError("ROOM_INVALID")
        if source_ref is not None:
            source_ref = clean_text(source_ref, "SOURCE_REF", 1024)
        metadata = metadata or {}
        if not isinstance(metadata, dict) or len(json.dumps(metadata)) > 4000:
            raise ValueError("METADATA_INVALID")
        eid = "ev_" + uuid.uuid4().hex
        when = utc_now()
        with self.lock, self._connect() as c:
            if not c.execute("SELECT 1 FROM rooms WHERE id=?", (room_id,)).fetchone():
                raise ValueError("ROOM_NOT_FOUND")
            c.execute("INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?)",
                      (eid,room_id,actor,role,kind,content,source_ref,
                       json.dumps(metadata,ensure_ascii=False),when))
        return {"id":eid,"room_id":room_id,"actor":actor,"role":role,"kind":kind,
                "content":content,"source_ref":source_ref,"metadata":metadata,"created_at":when}

    def events(self, room_id: str, limit: int = 100):
        if not isinstance(room_id,str) or len(room_id)>100:
            raise ValueError("ROOM_INVALID")
        limit=max(1,min(int(limit),200))
        with self.lock,self._connect() as c:
            rows=c.execute("SELECT * FROM events WHERE room_id=? ORDER BY created_at DESC,rowid DESC LIMIT ?",
                           (room_id,limit)).fetchall()
        return [dict(r,metadata=json.loads(r["metadata"])) for r in reversed(rows)]

    def search(self, query: str, limit: int = 8):
        query=clean_text(query,"QUERY",250)
        terms=[w.casefold() for w in re.findall(r"[\wÀ-ỹ]+",query,flags=re.UNICODE) if len(w)>1][:12]
        if not terms:
            raise ValueError("QUERY_TOO_SHORT")
        with self.lock,self._connect() as c:
            rows=c.execute("SELECT * FROM events ORDER BY created_at DESC,rowid DESC LIMIT 2000").fetchall()
        out=[]
        for row in rows:
            blob=(row["content"]+" "+(row["source_ref"] or "")).casefold()
            matched=[term for term in terms if term in blob]
            if matched:
                out.append({"event_id":row["id"],"room_id":row["room_id"],
                            "source_ref":row["source_ref"],"quote":row["content"][:320],
                            "matched_terms":matched,"observed_at":row["created_at"],
                            "score":len(matched)})
        out.sort(key=lambda e:-e["score"])
        return out[:max(1,min(int(limit),30))]

    def dispatch_offline(self, room_id: str, agent: str, task: str, route_callback=None):
        if agent not in {"researcher","analyst","router"}:
            raise ValueError("EXTERNAL_OR_UNAVAILABLE_AGENT_USE_CAPABILITY_GATE")
        task=clean_text(task,"TASK")
        assignment=self.add(room_id,"SOL","AM_PHAP_SU","assignment",
                            task,metadata={"specialist":agent,"state":"DISPATCHED"})
        if agent=="researcher":
            hits=self.search(task)
            output={"kind":"SOURCE_SEARCH","hits":hits,
                    "summary":"Search of previously recorded room events only; not web research."}
        elif agent=="analyst":
            from capabilities import analyze_text
            output=analyze_text(task)
        else:
            if route_callback is None:
                output={"state":"POWER_ROUTER_NOT_LOADED","next":"CHECK_PLUGINS_ROUTER"}
            else:
                output=route_callback(task)
        record=self.add(room_id,agent,"SPECIALIST_AGENT","result",
                        json.dumps(output,ensure_ascii=False)[:MAX_TEXT],
                        metadata={"assignment_id":assignment["id"],
                                  "scope":"LOCAL_EXECUTION_NOT_EXTERNAL_PROVIDER"})
        return {"assignment":assignment,"result":record,"output":output,
                "executed_locally":True,"external_provider_called":False}
