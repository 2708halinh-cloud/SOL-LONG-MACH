"""TESSERACT motherboard control-plane primitives (standard library only).
Adapters must supply real evidence; this module does not claim provider connectivity.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

class RouteState(str, Enum):
    READY = "READY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"

@dataclass(frozen=True)
class CpuSocket:
    socket_id: str
    name: str
    kind: str
    configured: bool = False
    reachable: bool = False
    authorized: bool = False
    quota_available: bool = True
    capabilities: tuple[str, ...] = ()

    @property
    def state(self) -> RouteState:
        if not (self.configured and self.reachable and self.authorized):
            return RouteState.UNAVAILABLE
        return RouteState.READY if self.quota_available else RouteState.DEGRADED

    def can_run(self, capability: str) -> bool:
        return self.state == RouteState.READY and capability in self.capabilities

@dataclass(frozen=True)
class DiskSafety:
    total_bytes: int
    free_bytes: int
    warning_used_percent: int = 90
    critical_used_percent: int = 97
    critical_free_bytes: int = 5 * 1024**3

    def __post_init__(self):
        if self.total_bytes <= 0 or not 0 <= self.free_bytes <= self.total_bytes:
            raise ValueError("invalid disk capacity")

    @property
    def used_percent(self) -> float:
        return 100.0 * (self.total_bytes - self.free_bytes) / self.total_bytes

    @property
    def level(self) -> str:
        if self.used_percent >= self.critical_used_percent or self.free_bytes < self.critical_free_bytes:
            return "CRITICAL"
        if self.used_percent >= self.warning_used_percent:
            return "SURVIVAL"
        return "NORMAL"

    @property
    def permits_nonessential_writes(self) -> bool:
        return self.level == "NORMAL"

@dataclass
class Blackboard:
    """Versioned transient shared state; rejects common credential-bearing fields."""
    version: int = 0
    registers: dict[str, Any] = field(default_factory=lambda: {
        "REG_00": {}, "REG_01": {}, "REG_02": {}, "REG_03": {"open_edges": []}
    })
    _FORBIDDEN_KEYS = {"token", "refresh_token", "cookie", "set_cookie", "authorization", "api_key", "apikey", "secret_value"}

    @classmethod
    def _check_fields(cls, value: Any, path: str = "root") -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                normalized = str(key).lower().replace("-", "_")
                if normalized in cls._FORBIDDEN_KEYS:
                    raise ValueError(f"credential material forbidden in blackboard: {path}.{key}")
                cls._check_fields(child, f"{path}.{key}")
        elif isinstance(value, (list, tuple)):
            for i, child in enumerate(value):
                cls._check_fields(child, f"{path}[{i}]")

    def update(self, register: str, value: Mapping[str, Any], expected_version: int) -> int:
        if register not in self.registers:
            raise KeyError(register)
        if expected_version != self.version:
            raise RuntimeError("BLACKBOARD_VERSION_CONFLICT")
        self._check_fields(value)
        self.registers[register] = dict(value)
        self.version += 1
        return self.version

@dataclass(frozen=True)
class GateDecision:
    allowed: bool
    reasons: tuple[str, ...]

def gate1_preflight(*, authorized: bool, target_identity_verified: bool,
                    policy_allowed: bool, quota_available: bool,
                    destructive_change: bool = False, protected_target: bool = False,
                    explicit_approval: bool = False) -> GateDecision:
    reasons = []
    if not authorized: reasons.append("NOT_AUTHORIZED")
    if not target_identity_verified: reasons.append("TARGET_IDENTITY_UNVERIFIED")
    if not policy_allowed: reasons.append("POLICY_BLOCK")
    if not quota_available: reasons.append("QUOTA_UNAVAILABLE")
    if destructive_change and protected_target: reasons.append("PROTECTED_TARGET")
    if destructive_change and not explicit_approval: reasons.append("EXPLICIT_APPROVAL_REQUIRED")
    return GateDecision(not reasons, tuple(reasons))

def gate2_readback(*, action_receipt: bool, consequence_observed: bool,
                   independent_readback: bool, state_consistent: bool) -> GateDecision:
    missing = []
    if not action_receipt: missing.append("RECEIPT_MISSING")
    if not consequence_observed: missing.append("CONSEQUENCE_UNOBSERVED")
    if not independent_readback: missing.append("READBACK_MISSING")
    if not state_consistent: missing.append("STATE_MISMATCH")
    return GateDecision(not missing, tuple(missing))

@dataclass(frozen=True)
class AffectEvent:
    signal: str
    context: str
    observed_facts: tuple[str, ...] = ()
    cause_hypotheses: tuple[str, ...] = ()
    intensity: float | None = None
    recurrence_key: str | None = None

    def __post_init__(self):
        if not self.signal.strip() or not self.context.strip():
            raise ValueError("affect signal and context must be preserved")
        if self.intensity is not None and not 0.0 <= self.intensity <= 1.0:
            raise ValueError("intensity must be in [0, 1]")

def route_candidates(sockets: list[CpuSocket], capability: str,
                     prefer_local: bool = True) -> list[CpuSocket]:
    eligible = [s for s in sockets if s.can_run(capability)]
    return sorted(eligible, key=lambda s: (0 if prefer_local and s.name == "LOCAL" else 1, s.socket_id))

[executed on device: DESKTOP-86ITNQ4 (bca58242-9cf0-407e-afb4-fb9ecfcce34b)]