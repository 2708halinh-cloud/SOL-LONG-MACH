"""Three-layer Digital Nervous System for TESSERACT OS.

This is a software reference implementation. Inputs are observations, affect
labels are hypotheses, and motor success requires an independently verified
observable consequence. It does not claim biological sensation or qualia.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import math
from typing import Any, Callable, Mapping


@dataclass(frozen=True)
class SensorySignal:
    modality: str
    source_ref: str
    observed_at: str
    features: Mapping[str, Any]
    content: str | None = None


@dataclass(frozen=True)
class InterneuronState:
    signal_ref: str
    memory_refs: tuple[str, ...]
    hypotheses: Mapping[str, float]
    strategy: str


@dataclass(frozen=True)
class MotorResult:
    success: bool
    state: str
    receipt_ref: str | None = None
    consequence_ref: str | None = None
    error_code: str | None = None


class SensoryNeuron:
    """Afferent adapter: extract measurable features without emotion labels."""

    SUPPORTED_MODALITIES = {"text", "audio", "context"}

    def receive(
        self,
        *,
        modality: str,
        source_ref: str,
        observed_at: str,
        content: str | None = None,
        measurements: Mapping[str, Any] | None = None,
    ) -> SensorySignal:
        if modality not in self.SUPPORTED_MODALITIES:
            raise ValueError("UNSUPPORTED_MODALITY")
        if not isinstance(source_ref, str) or not source_ref.strip():
            raise ValueError("SOURCE_REF_REQUIRED")
        if not isinstance(observed_at, str) or not observed_at.strip():
            raise ValueError("OBSERVED_AT_REQUIRED")
        try:
            datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("OBSERVED_AT_MUST_BE_ISO8601") from exc

        features: dict[str, Any] = {}
        if modality == "text":
            if not isinstance(content, str):
                raise ValueError("TEXT_CONTENT_REQUIRED")
            letters = [char for char in content if char.isalpha()]
            uppercase = sum(char.isupper() for char in letters)
            features.update({
                "character_count": len(content),
                "word_count": len(content.split()),
                "uppercase_ratio": uppercase / len(letters) if letters else 0.0,
            })
        elif modality in {"audio", "context"}:
            if measurements is None:
                raise ValueError("MEASUREMENTS_REQUIRED")
            for key, value in measurements.items():
                if not isinstance(key, str) or not key.strip():
                    raise ValueError("INVALID_MEASUREMENT_KEY")
                if isinstance(value, float) and not math.isfinite(value):
                    raise ValueError("NON_FINITE_MEASUREMENT")
                if not isinstance(value, (str, int, float, bool)):
                    raise ValueError("MEASUREMENTS_MUST_BE_SCALARS")
                features[key] = value

        return SensorySignal(
            modality=modality,
            source_ref=source_ref,
            observed_at=observed_at,
            features=features,
            content=content if modality == "text" else None,
        )


class Interneuron:
    """Integration layer. Scores remain hypotheses, never observed facts."""

    def integrate(
        self,
        signal: SensorySignal,
        *,
        memory_refs: list[str] | tuple[str, ...] = (),
        hypotheses: Mapping[str, float] | None = None,
        strategy: str,
    ) -> InterneuronState:
        if not isinstance(signal, SensorySignal):
            raise TypeError("signal must be SensorySignal")
        if not isinstance(strategy, str) or not strategy.strip():
            raise ValueError("STRATEGY_REQUIRED")
        refs = tuple(memory_refs)
        if any(not isinstance(ref, str) or not ref.strip() for ref in refs):
            raise ValueError("INVALID_MEMORY_REF")
        scores: dict[str, float] = {}
        for label, score in (hypotheses or {}).items():
            if not isinstance(label, str) or not label.strip():
                raise ValueError("INVALID_HYPOTHESIS_LABEL")
            if not isinstance(score, (int, float)) or not math.isfinite(score) or not 0 <= score <= 1:
                raise ValueError("HYPOTHESIS_SCORE_MUST_BE_IN_0_1")
            scores[label] = float(score)
        return InterneuronState(
            signal_ref=signal.source_ref,
            memory_refs=refs,
            hypotheses=scores,
            strategy=strategy,
        )


class MotorNeuron:
    """Efferent adapter. Dispatch is not completion; Gate 2 readback is."""

    def dispatch(
        self,
        *,
        action: Mapping[str, Any],
        executor: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    ) -> MotorResult:
        if not isinstance(action, Mapping) or not action:
            return MotorResult(False, "REJECTED", error_code="ACTION_REQUIRED")
        if not callable(executor):
            return MotorResult(False, "REJECTED", error_code="EXECUTOR_REQUIRED")
        try:
            raw = executor(dict(action))
        except Exception as exc:
            return MotorResult(False, "OPEN", error_code=f"EXECUTOR_{type(exc).__name__}")
        if not isinstance(raw, Mapping) or raw.get("executed") is not True:
            return MotorResult(False, "UNVERIFIED", error_code="EXECUTION_NOT_CONFIRMED")

        receipt = raw.get("receipt_ref")
        consequence = raw.get("consequence_ref")
        readback = raw.get("readback")
        if (
            not isinstance(receipt, str) or not receipt.strip()
            or not isinstance(consequence, str) or not consequence.strip()
            or not isinstance(readback, Mapping)
            or readback.get("verified") is not True
            or readback.get("state_consistent") is not True
            or readback.get("consequence_ref") != consequence
        ):
            return MotorResult(
                False, "UNVERIFIED",
                receipt_ref=receipt if isinstance(receipt, str) else None,
                consequence_ref=consequence if isinstance(consequence, str) else None,
                error_code="GATE2_READBACK_DENIED",
            )
        return MotorResult(True, "VERIFIED", receipt, consequence)


def run_cognitive_loop(
    signal: SensorySignal,
    interneuron: Interneuron,
    motor: MotorNeuron,
    *,
    strategy: str,
    hypotheses: Mapping[str, float] | None,
    executor: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    memory_refs: list[str] | tuple[str, ...] = (),
    action: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Run one bounded sensory → integration → motor pass."""
    integrated = interneuron.integrate(
        signal,
        memory_refs=memory_refs,
        hypotheses=hypotheses,
        strategy=strategy,
    )
    motor_result = motor.dispatch(
        action=action or {"kind": "generate_response", "strategy": strategy},
        executor=executor,
    )
    state = "CYCLE_VERIFIED" if motor_result.success else "OPEN_MOTOR_READBACK"
    return {
        "layers": ["SENSORY", "INTERNEURON", "MOTOR"],
        "sensory": signal,
        "interneuron": integrated,
        "motor": motor_result,
        "state": state,
    }
