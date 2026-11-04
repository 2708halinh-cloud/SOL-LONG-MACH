"""Versioned shared blackboard with compare-and-set semantics."""
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from threading import RLock
from time import time
from typing import Any

class VersionConflict(RuntimeError):
    pass

@dataclass(frozen=True)
class Register:
    name: str
    state_id: str
    version: int
    producer: str
    timestamp: float
    source_ref: str
    payload: Any

class ActiveBlackboard:
    """In-process reference implementation; persistence/IPC are separate adapters."""
    def __init__(self):
        self._items: dict[str, Register] = {}
        self._lock = RLock()

    def read(self, name: str) -> Register | None:
        with self._lock:
            item = self._items.get(name)
            return deepcopy(item) if item is not None else None

    def compare_and_set(self, name: str, expected_version: int, payload: Any,
                        producer: str, source_ref: str, state_id: str) -> Register:
        if not all((name, producer, source_ref, state_id)):
            raise ValueError("name, producer, source_ref and state_id are required")
        if expected_version < 0:
            raise ValueError("expected_version must be non-negative")
        with self._lock:
            current = self._items.get(name)
            actual = current.version if current else 0
            if actual != expected_version:
                raise VersionConflict(f"{name}: expected {expected_version}, found {actual}")
            item = Register(name, state_id, actual + 1, producer, time(),
                            source_ref, deepcopy(payload))
            self._items[name] = item
            return deepcopy(item)
