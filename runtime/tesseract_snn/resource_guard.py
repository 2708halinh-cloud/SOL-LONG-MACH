"""Disk-capacity guard with stale/unknown fail-closed behavior."""
from dataclasses import dataclass

GIB = 1024 ** 3

@dataclass(frozen=True)
class DiskSample:
    total_bytes: int
    free_bytes: int
    fresh: bool = True

@dataclass(frozen=True)
class GuardResult:
    mode: str
    used_percent: float | None
    reason: str

class DiskGuard:
    def __init__(self, absolute_free_floor: int = 5 * GIB):
        if absolute_free_floor < 0: raise ValueError("free-space floor must be non-negative")
        self.absolute_free_floor = absolute_free_floor
        self.degraded = False
        self._recovery_samples = 0

    def evaluate(self, sample: DiskSample) -> GuardResult:
        if (not sample.fresh or sample.total_bytes <= 0 or sample.free_bytes < 0
                or sample.free_bytes > sample.total_bytes):
            self.degraded = True
            self._recovery_samples = 0
            return GuardResult("DEGRADED", None, "capacity measurement is unknown or invalid")
        used = 100.0 * (sample.total_bytes - sample.free_bytes) / sample.total_bytes
        if used >= 90.0 or sample.free_bytes < self.absolute_free_floor:
            self.degraded = True
            self._recovery_samples = 0
            return GuardResult("DEGRADED", used, "trip threshold reached")
        if self.degraded:
            if used <= 85.0 and sample.free_bytes >= self.absolute_free_floor:
                self._recovery_samples += 1
                if self._recovery_samples >= 2:
                    self.degraded = False
                    self._recovery_samples = 0
                    return GuardResult("NORMAL", used, "recovered after two safe samples")
            else:
                self._recovery_samples = 0
            return GuardResult("DEGRADED", used, "waiting for recovery hysteresis")
        if used >= 85.0:
            return GuardResult("WARNING", used, "warning threshold reached")
        return GuardResult("NORMAL", used, "capacity within policy")
