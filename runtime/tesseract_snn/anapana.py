"ANAPANA asynchronous substrate telemetry loop.

The loop is independent of chat requests while its host service remains alive.
Sensor acquisition is injected; no hardware metric is fabricated by this module.
"""
from __future__ import annotations
import asyncio
from collections import deque
from dataclasses import dataclass
from typing import Awaitable, Callable

@dataclass(frozen=True)
class TelemetrySnapshot:
    timestamp: float
    cpu_load: float | None
    memory_used_bytes: int | None
    memory_total_bytes: int | None
    disk_free_bytes: int | None
    cpu_temperature_c: float | None = None

    def validate(self) -> None:
        if self.cpu_load is not None and not 0.0 <= self.cpu_load <= 1.0:
            raise ValueError("cpu_load must be normalized to [0, 1]")
        if self.memory_used_bytes is not None and self.memory_used_bytes < 0:
            raise ValueError("memory_used_bytes must be non-negative")
        if self.memory_total_bytes is not None and self.memory_total_bytes <= 0:
            raise ValueError("memory_total_bytes must be positive")
        if self.disk_free_bytes is not None and self.disk_free_bytes < 0:
            raise ValueError("disk_free_bytes must be non-negative")

Sensor = Callable[[], Awaitable[TelemetrySnapshot]]
Observer = Callable[[TelemetrySnapshot], Awaitable[None]]

class AnapanaMonitor:
    def __init__(self, sensor: Sensor, interval_seconds: float = 1.0,
                 history_limit: int = 256, observer: Observer | None = None):
        if interval_seconds <= 0: raise ValueError("interval_seconds must be positive")
        if history_limit < 1: raise ValueError("history_limit must be positive")
        self.sensor, self.interval_seconds = sensor, interval_seconds
        self.history = deque(maxlen=history_limit)
        self.observer = observer
        self._stop: asyncio.Event | None = None
        self._task: asyncio.Task | None = None
        self._active = False

    @property
    def running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def run(self) -> None:
        """Run until stop() is requested or the sensor/observer raises."""
        if self._active: raise RuntimeError("ANAPANA monitor is already running")
        self._active = True
        if self._stop is None:
            self._stop = asyncio.Event()
        try:
            while not self._stop.is_set():
                sample = await self.sensor()
                sample.validate()
                self.history.append(sample)
                if self.observer is not None:
                    await self.observer(sample)
                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=self.interval_seconds)
                except asyncio.TimeoutError:
                    pass
        finally:
            self._active = False

    def start(self) -> asyncio.Task:
        if self.running: raise RuntimeError("ANAPANA monitor is already running")
        self._stop = asyncio.Event()
        self._task = asyncio.create_task(self.run(), name="tesseract-anapana")
        return self._task

    async def stop(self) -> None:
        if self._stop is not None:
            self._stop.set()
        if self._task is not None:
            await self._task
            self._task = None
