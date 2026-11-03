"""TESSERACT motherboard control-plane primitives (standard library only).
Adapters must supply real evidence; this module does not claim provider connectivity.
"""
from __future__ import annotations
from copy import deepcopy
import re
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
    """Classify one capacity sample; use DiskWriteGuard for write decisions."""
    total_bytes: int
    free_bytes: int
    warning_used_percent: float = 85.0
    critical_used_percent: float = 90.0
    critical_free_bytes: int = 5 * 1024**3

    def __post_init__(self):
        if self.total_bytes <= 0 or not 0 <= self.free_bytes <= self.total_bytes:
            raise ValueError("invalid disk capacity")
        if not 0 <= self.warning_used_percent < self.critical_used_percent <= 100:
            raise ValueError("disk thresholds must satisfy 0 <= warning < critical <= 100")
        if self.critical_free_bytes < 0:
            raise ValueError("critical_free_bytes must be non-negative")

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
        # Warning at 85% is not the trip point; the guard trips at 90% or the absolute free-space floor.
        return self.level != "CRITICAL"


@dataclass
class DiskWriteGuard:
    """Stateful disk policy: stale/unknown samples fail closed; recovery needs two fresh safe samples."""
    warning_used_percent: float = 85.0
    critical_used_percent: float = 90.0
    recovery_used_percent: float = 85.0
    recovery_samples_required: int = 2
    critical_free_bytes: int = 5 * 1024**3
    _degraded: bool = field(default=False, init=False, repr=False)
    _unknown: bool = field(default=False, init=False, repr=False)
    _recovery_streak: int = field(default=0, init=False, repr=False)
    _last_level: str = field(default="UNKNOWN", init=False, repr=False)

    def __post_init__(self):
        if not 0 <= self.recovery_used_percent <= self.warning_used_percent < self.critical_used_percent <= 100:
            raise ValueError("disk thresholds must satisfy 0 <= recovery <= warning < critical <= 100")
        if self.recovery_samples_required < 1 or self.critical_free_bytes < 0:
            raise ValueError("recovery sample count and free-space floor must be valid")

    @property
    def level(self) -> str:
        if self._unknown:
            return "UNKNOWN"
        if self._degraded:
            return "DEGRADED"
        return self._last_level

    @property
    def permits_nonessential_writes(self) -> bool:
        return not self._degraded and not self._unknown

    @property
    def recovery_streak(self) -> int:
        return self._recovery_streak

    def observe(self, total_bytes: int | None, free_bytes: int | None, *, sample_fresh: bool = False) -> str:
        # Freshness is an explicit caller attestation. Missing, stale, or invalid measurements fail closed.
        if (
            not sample_fresh
            or total_bytes is None
            or free_bytes is None
            or total_bytes <= 0
            or free_bytes < 0
            or free_bytes > total_bytes
        ):
            self._unknown = True
            self._degraded = True
            self._recovery_streak = 0
            self._last_level = "UNKNOWN"
            return self.level

        snapshot = DiskSafety(
            total_bytes,
            free_bytes,
            warning_used_percent=self.warning_used_percent,
            critical_used_percent=self.critical_used_percent,
            critical_free_bytes=self.critical_free_bytes,
        )
        self._unknown = False
        if snapshot.level == "CRITICAL":
            self._degraded = True
            self._recovery_streak = 0
            self._last_level = "DEGRADED"
            return self.level

        if self._degraded:
            if snapshot.used_percent <= self.recovery_used_percent and free_bytes >= self.critical_free_bytes:
                self._recovery_streak += 1
                if self._recovery_streak >= self.recovery_samples_required:
                    self._degraded = False
                    self._recovery_streak = 0
            else:
                self._recovery_streak = 0

        self._last_level = "SURVIVAL" if snapshot.level == "SURVIVAL" else "NORMAL"
        return self.level

@dataclass
class Blackboard:
    """Versioned transient shared state; rejects common credential-bearing fields."""
    version: int = 0
    registers: dict[str, Any] = field(default_factory=lambda: {
        "REG_00": {}, "REG_01": {}, "REG_02": {}, "REG_03": {"open_edges": []}
    })
    _FORBIDDEN_KEYS = {
        "token", "access_token", "refresh_token", "id_token", "auth_token",
        "cookie", "set_cookie", "authorization", "authorization_header", "auth_header",
        "api_key", "apikey", "secret", "secret_value", "secret_key",
        "password", "passwd", "credential", "credentials", "private_key",
        "signing_key", "client_secret",
    }
    _FORBIDDEN_SUFFIXES = (
        "_token", "_secret", "_password", "_passwd", "_credential",
        "_credentials", "_api_key", "_private_key", "_signing_key",
    )
    _FORBIDDEN_PREFIXES = ("secret_", "credential_", "credentials_", "token_")

    @classmethod
    def _normalize_key(cls, key: Any) -> str:
        raw = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str(key))
        return raw.lower().replace("-", "_").replace(" ", "_")

    @classmethod
    def _is_forbidden_key(cls, key: Any) -> bool:
        normalized = cls._normalize_key(key)
        return (
            normalized in cls._FORBIDDEN_KEYS
            or normalized.startswith(cls._FORBIDDEN_PREFIXES)
            or normalized.endswith(cls._FORBIDDEN_SUFFIXES)
            or "_secret_" in normalized
            or "_credential_" in normalized
        )

    @classmethod
    def _check_fields(cls, value: Any, path: str = "root") -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                if cls._is_forbidden_key(key):
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
        snapshot = deepcopy(dict(value))
        self._check_fields(snapshot)
        self.registers[register] = snapshot
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
