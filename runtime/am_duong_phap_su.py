#!/usr/bin/env python3
"""Âm Dương Pháp Sư: a declarative DSL over TESSERACT's two gates.

ÂM supplies provenance, identity, authorization and stable constraints.
DƯƠNG supplies candidate neurons and executable behavior.
TÂM evaluates gate conditions before any neuron fires.
STAMP_OLD is emitted only after Gate 2 readback succeeds.

The bootstrap router uses deterministic token similarity, not a fake embedding.
This module does not claim consciousness, modify model weights, or self-schedule.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable

try:
    from .motherboard_control_plane import gate1_preflight, gate2_readback
except ImportError:
    from motherboard_control_plane import gate1_preflight, gate2_readback


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[\wÀ-ỹ]+", value.casefold(), flags=re.UNICODE))


def semantic_potential(signal: str, description: str) -> float:
    """Deterministic Jaccard bootstrap; replace via a verified embedding adapter."""
    left, right = _tokens(signal), _tokens(description)
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


@dataclass(frozen=True)
class ActionEvidence:
    """Evidence returned by an adapter after it performs and reads back an action."""
    output: dict[str, Any]
    action_receipt: bool
    consequence_observed: bool
    independent_readback: bool
    state_consistent: bool


@dataclass(frozen=True)
class Neuron:
    name: str
    description: str
    execute: Callable[[dict[str, Any]], ActionEvidence]
    side_effect: bool = False


@dataclass(frozen=True)
class Stamp:
    kind: str
    run_id: str
    payload: dict[str, Any]


@dataclass
class Tran:
    """One declarative trận. The Unicode method names are the DSL vocabulary."""
    run_id: str
    signal: str
    source_ref: str = ""
    author: str = ""
    platform: str = ""
    authorized: bool = False
    target_verified: bool = False
    policy_allowed: bool = False
    quota_available: bool = False
    explicit_approval: bool = False
    protected_target: bool = False
    neurons: list[Neuron] = field(default_factory=list)
    hypotheses: list[str] = field(default_factory=list)

    def ÂM(self, *, source_ref: str, author: str = "", platform: str = "",
          authorized: bool = False, target_verified: bool = False) -> "Tran":
        self.source_ref = source_ref
        self.author = author
        self.platform = platform
        self.authorized = authorized
        self.target_verified = target_verified
        return self

    def DƯƠNG(self, *neurons: Neuron) -> "Tran":
        self.neurons.extend(neurons)
        return self

    def TÂM(self, *, policy_allowed: bool, quota_available: bool = True,
            explicit_approval: bool = False, protected_target: bool = False) -> "Tran":
        self.policy_allowed = policy_allowed
        self.quota_available = quota_available
        self.explicit_approval = explicit_approval
        self.protected_target = protected_target
        return self

    def GIẢ_THUYẾT(self, *hypotheses: str) -> "Tran":
        self.hypotheses.extend(x for x in hypotheses if x and x.strip())
        return self


@dataclass
class TranResult:
    run_id: str
    status: str
    selected_neuron: str | None
    potential: float | None
    output: dict[str, Any]
    stamps: list[Stamp]
    gate_reasons: tuple[str, ...] = ()


class AmDuongPhapSu:
    """Runs one bounded cycle; it never busy-spins or self-schedules forever."""
    def __init__(self, *, threshold: float = 0.25):
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0 and 1")
        self.threshold = threshold
        self._seen_run_ids: set[str] = set()
        self._neurons: dict[str, Neuron] = {}

    def register(self, neuron: Neuron) -> None:
        if not neuron.name.strip() or not neuron.description.strip():
            raise ValueError("neuron name and description are required")
        if neuron.name in self._neurons:
            raise ValueError(f"duplicate neuron: {neuron.name}")
        self._neurons[neuron.name] = neuron

    def khai_trận(self, tran: Tran) -> TranResult:
        if not tran.run_id.strip() or not tran.signal.strip() or not tran.source_ref.strip():
            raise ValueError("run_id, signal and source_ref are required")
        if tran.run_id in self._seen_run_ids:
            raise ValueError(f"duplicate run_id: {tran.run_id}")
        self._seen_run_ids.add(tran.run_id)

        stamps = [Stamp("STAMP_LIVE", tran.run_id, {
            "signal": tran.signal, "source_ref": tran.source_ref,
            "author": tran.author, "platform": tran.platform,
        })]
        stamps.extend(Stamp("STAMP_BETA", tran.run_id, {"hypothesis": h})
                      for h in tran.hypotheses)

        candidates = [(semantic_potential(tran.signal, neuron.description), neuron)
                      for neuron in (tran.neurons or list(self._neurons.values()))]
        candidates = [(score, neuron) for score, neuron in candidates
                      if score >= self.threshold]
        if not candidates:
            return TranResult(tran.run_id, "NO_NEURON_MATCH", None, None, {}, stamps)
        candidates.sort(key=lambda item: (-item[0], item[1].name))
        score, neuron = candidates[0]

        gate1 = gate1_preflight(
            authorized=tran.authorized,
            target_identity_verified=tran.target_verified,
            policy_allowed=tran.policy_allowed,
            quota_available=tran.quota_available,
            destructive_change=neuron.side_effect,
            protected_target=tran.protected_target,
            explicit_approval=tran.explicit_approval,
        )
        if not gate1.allowed:
            return TranResult(tran.run_id, "GATE1_REJECTED", neuron.name,
                              score, {}, stamps, gate1.reasons)

        evidence = neuron.execute({
            "run_id": tran.run_id, "signal": tran.signal,
            "source_ref": tran.source_ref, "author": tran.author,
            "platform": tran.platform, "semantic_potential": score,
        })
        if not isinstance(evidence, ActionEvidence):
            raise TypeError("neuron must return ActionEvidence")

        gate2 = gate2_readback(
            action_receipt=evidence.action_receipt,
            consequence_observed=evidence.consequence_observed,
            independent_readback=evidence.independent_readback,
            state_consistent=evidence.state_consistent,
        )
        if not gate2.allowed:
            return TranResult(tran.run_id, "READBACK_REJECTED", neuron.name,
                              score, evidence.output, stamps, gate2.reasons)

        stamps.append(Stamp("STAMP_OLD", tran.run_id, {
            "neuron": neuron.name, "output": evidence.output,
            "source_ref": tran.source_ref, "semantic_potential": score,
            "receipt": evidence.action_receipt,
            "consequence": evidence.consequence_observed,
            "independent_readback": evidence.independent_readback,
            "state_consistent": evidence.state_consistent,
        }))
        return TranResult(tran.run_id, "COMPLETED", neuron.name, score,
                          evidence.output, stamps)
