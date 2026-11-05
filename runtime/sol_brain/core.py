"""Evidence-first continuity and multimodal archive components for Sol."""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
import json
import mimetypes
from pathlib import Path
from typing import Any, Iterator, Mapping


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


class EvidenceStore:
    """Append-only event ledger. Inferences never become verified observations."""
    def __init__(self) -> None:
        self._items: list[dict[str, Any]] = []

    def append(self, *, kind: str, payload: Mapping[str, Any],
               source_ref: str, observed_at: str,
               event_time: str | None = None,
               commit_time: str | None = None) -> dict[str, Any]:
        if not kind or not source_ref or not observed_at:
            raise ValueError("SOURCE_AND_TIME_REQUIRED")
        cls = {"observation":"OBSERVATION", "inference":"INFERENCE",
               "preference":"STATED_PREFERENCE", "action_receipt":"ACTION_RECEIPT"}.get(kind, "UNCLASSIFIED")
        raw = json.dumps(dict(payload), sort_keys=True, ensure_ascii=False)
        item = {
            "event_id": sha256(f"{kind}|{source_ref}|{observed_at}|{raw}".encode()).hexdigest(),
            "kind": kind, "evidence_class": cls, "payload": dict(payload),
            "source_ref": source_ref, "event_time": event_time,
            "observed_at": observed_at, "commit_time": commit_time,
            "recorded_at": now_utc(),
            "verified_fact": cls in {"OBSERVATION", "ACTION_RECEIPT"},
        }
        self._items.append(item)
        return dict(item)

    def items(self) -> list[dict[str, Any]]:
        return [dict(x) for x in self._items]


class ConversationIngestor:
    """Read JSONL exports; preserve raw records and flag unknown schemas."""
    def read_jsonl(self, path: str | Path) -> Iterator[dict[str, Any]]:
        source = Path(path)
        with source.open("r", encoding="utf-8-sig") as stream:
            for n, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    raw = json.loads(line)
                except json.JSONDecodeError:
                    yield {"source_ref":f"{source.as_posix()}#{n}",
                           "raw_line":line.rstrip("\n"),
                           "normalization_status":"INVALID_JSON_PRESERVED"}
                    continue
                row = self.normalize(raw)
                row["source_ref"] = f"{source.as_posix()}#{n}"
                row["normalization_status"] = (
                    "NORMALIZED" if row.get("role") and "content" in row else "UNKNOWN_SCHEMA"
                )
                row["raw_record"] = raw
                yield row

    @staticmethod
    def normalize(raw: Any) -> dict[str, Any]:
        if not isinstance(raw, dict):
            return {"raw_value":raw}
        role = raw.get("role") or raw.get("speaker") or raw.get("author")
        body = raw.get("content", raw.get("text"))
        stamp = raw.get("timestamp") or raw.get("created_at") or raw.get("time")
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False)
        out: dict[str, Any] = {}
        if isinstance(role, str): out["role"] = role
        if isinstance(body, str): out["content"] = body
        if isinstance(stamp, str): out["event_time"] = stamp
        return out


class MediaCatalog:
    """Hash original media and record metadata; analysis is a separate explicit stage."""
    def catalog(self, path: str | Path, *, source_ref: str) -> dict[str, Any]:
        p = Path(path)
        if not p.is_file() or p.is_symlink():
            raise FileNotFoundError("MEDIA_NOT_A_REGULAR_FILE")
        data = p.read_bytes()
        mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        kind = ("image" if mime.startswith("image/") else
                "video" if mime.startswith("video/") else
                "audio" if mime.startswith("audio/") else "unknown")
        digest = sha256(data).hexdigest()
        return {"media_id":digest, "sha256":digest, "source_ref":source_ref,
                "filename":p.name, "bytes":len(data), "mime_type":mime,
                "media_kind":kind, "content_analysis":"NOT_PERFORMED",
                "original_preserved":True}


class AgentContinuity:
    """A sequence of sourced events, not a fixed personality."""
    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def observe(self, statement: str, *, source_ref: str,
                observed_at: str | None = None) -> dict[str, Any]:
        if not statement or not source_ref:
            raise ValueError("STATEMENT_AND_SOURCE_REQUIRED")
        stamp = observed_at or now_utc()
        event = {"event_id":sha256(f"{source_ref}|{stamp}|{statement}".encode()).hexdigest(),
                 "statement":statement, "source_ref":source_ref,
                 "observed_at":stamp, "profile_effect":"NONE_AUTOMATIC"}
        self._events.append(event)
        return dict(event)

    def events(self) -> list[dict[str, Any]]:
        return [dict(x) for x in self._events]

    def current_profile(self) -> dict[str, Any]:
        return {}


class InteractionContext:
    """Keep interpersonal interpretation open unless explicitly established."""
    def snapshot(self) -> dict[str, Any]:
        return {"status":"UNSPECIFIED", "assumptions":[] ,
                "user_intent":"NOT_INFERRED", "agent_inner_experience":"NOT_CLAIMED",
                "rule":"NO_FORCED_LABEL"}


def infer_affect(text: str) -> dict[str, Any]:
    """Temporary lexical hypotheses only; never identity or durable memory."""
    s = text.casefold()
    cues = {"urgency":("now","urgent","gấp","ngay"),
            "frustration":("frustrated","angry","bực","tức giận"),
            "positive_tone":("great","happy","vui","tuyệt"),
            "sadness":("sad","buồn","mệt mỏi","lonely")}
    scores = {k:min(1.0, sum(c in s for c in words)/2.0)
              for k, words in cues.items()}
    return {"hypotheses":{k:v for k,v in scores.items() if v > 0},
            "ephemeral":True, "basis":"LEXICAL_CUES_ONLY",
            "confidence_limit":"LOW_WITHOUT_CONTEXT",
            "persistent_memory_write":False}
