"""Preallocated fixed-size scratch buffers for bounded-memory tool workloads.

This is a runtime preallocation pool, not compile-time static allocation.
It prevents repeated large payload-buffer allocation when callers use memoryviews
and readinto/write APIs; Python may still allocate small metadata objects.

STAMP_LIVE_X: 2026-10-27 (UTC+07:00; minute not independently measured)
SOURCE_ID: SOL-LONG-MACH / ChatGPT Library / OS_WORK/tools
ACTOR: Hà Linh (design source); SOL (implementation and verification)
ACTIVE: TRUE
PROVENANCE: Added on feature/static-memory-allocation-library after tests were committed.
"""
from __future__ import annotations

from threading import Lock
from typing import Final


class BufferPoolExhausted(RuntimeError):
    """Raised when all preallocated buffers are currently leased."""


class FixedBufferPool:
    """A bounded pool of preallocated bytearrays.

    Each acquire returns a memoryview over an existing bytearray. Callers must
    release every acquired view, preferably in a try/finally block. The pool
    never grows implicitly: exhaustion is visible and deterministic.
    """

    __slots__ = ("_buffers", "_free", "_leased", "_lock", "buffer_size")

    def __init__(self, buffer_count: int, buffer_size: int) -> None:
        if isinstance(buffer_count, bool) or not isinstance(buffer_count, int) or buffer_count <= 0:
            raise ValueError("buffer_count must be a positive integer")
        if isinstance(buffer_size, bool) or not isinstance(buffer_size, int) or buffer_size <= 0:
            raise ValueError("buffer_size must be a positive integer")

        self._buffers: Final[list[bytearray]] = [
            bytearray(buffer_size) for _ in range(buffer_count)
        ]
        self._free = list(range(buffer_count))
        self._leased: set[int] = set()
        self._lock = Lock()
        self.buffer_size = buffer_size

    @property
    def capacity_bytes(self) -> int:
        """Total scratch-buffer capacity reserved at pool construction."""
        return len(self._buffers) * self.buffer_size

    @property
    def available_count(self) -> int:
        with self._lock:
            return len(self._free)

    def acquire(self) -> memoryview:
        """Lease one existing buffer without allocating a new payload buffer."""
        with self._lock:
            if not self._free:
                raise BufferPoolExhausted(
                    f"fixed buffer pool exhausted: {len(self._leased)} leased, "
                    f"{len(self._buffers)} total"
                )
            index = self._free.pop()
            self._leased.add(index)
            return memoryview(self._buffers[index])

    def release(self, view: memoryview) -> None:
        """Return a leased view to the pool; reject foreign or duplicate releases."""
        if not isinstance(view, memoryview):
            raise ValueError("release expects a memoryview returned by acquire()")
        try:
            backing = view.obj
        except ValueError as exc:
            raise ValueError("view has already been released") from exc

        with self._lock:
            index = next(
                (i for i, buffer in enumerate(self._buffers) if backing is buffer),
                None,
            )
            if index is None:
                raise ValueError("view does not belong to this pool")
            if index not in self._leased:
                raise ValueError("buffer is not currently leased")

            self._leased.remove(index)
            self._free.append(index)
            view.release()

    def __enter__(self) -> "FixedBufferPool":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        with self._lock:
            if self._leased:
                raise RuntimeError(
                    f"fixed buffer pool closed with {len(self._leased)} outstanding lease(s)"
                )
