"""Append-only JSONL hash-chain journal with readback verification."""
from __future__ import annotations
import hashlib, json, os
from pathlib import Path
from typing import Any

GENESIS = "0" * 64

class AppendOnlyJournal:
    def __init__(self, path: str | os.PathLike):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    @staticmethod
    def _canonical(value: dict[str, Any]) -> bytes:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")

    def append(self, event: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(event, dict) or not event:
            raise ValueError("event must be a non-empty object")
        records = self.read_all()
        previous = records[-1]["record_hash"] if records else GENESIS
        body = {"sequence": len(records) + 1, "previous_hash": previous, "event": event}
        digest = hashlib.sha256(self._canonical(body)).hexdigest()
        record = {**body, "record_hash": digest}
        line = self._canonical(record) + b"\n"
        with self.path.open("ab") as stream:
            stream.write(line)
            stream.flush()
            os.fsync(stream.fileno())
        return record

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists() or self.path.stat().st_size == 0:
            return []
        records = []
        for line_number, line in enumerate(self.path.read_bytes().splitlines(), 1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid journal line {line_number}") from exc
            records.append(record)
        return records

    def verify(self) -> bool:
        previous = GENESIS
        for expected_sequence, record in enumerate(self.read_all(), 1):
            body = {k: record[k] for k in ("sequence", "previous_hash", "event")}
            if record["sequence"] != expected_sequence or record["previous_hash"] != previous:
                return False
            digest = hashlib.sha256(self._canonical(body)).hexdigest()
            if digest != record.get("record_hash"):
                return False
            previous = digest
        return True
