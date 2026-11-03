"""Deterministic CPU reference engine for TESSERACT's event-driven sparse SNN."""
from __future__ import annotations

from dataclasses import dataclass, field
import heapq
import math
from typing import List, Optional


@dataclass
class Neuron:
    threshold: float = 1.0
    leak: float = 0.95
    membrane: float = 0.0
    refractory_until: int = 0
    alive: bool = True
    spikes: int = 0
    last_update_tick: int = 0

    def __post_init__(self):
        if not math.isfinite(self.threshold) or self.threshold <= 0:
            raise ValueError("threshold must be finite and positive")
        if not math.isfinite(self.leak) or not 0 <= self.leak <= 1:
            raise ValueError("leak must be in [0, 1]")
        if not math.isfinite(self.membrane):
            raise ValueError("membrane must be finite")
        if self.last_update_tick < 0:
            raise ValueError("last_update_tick must be non-negative")


@dataclass
class Synapse:
    source: int
    target: int
    weight: float
    delay: int = 1
    momentum: float = 0.0
    active: bool = True
    stable_cycles: int = 0
    invariant: bool = False

    def __post_init__(self):
        if not math.isfinite(self.weight) or not math.isfinite(self.momentum):
            raise ValueError("synapse state must be finite")
        if self.delay < 1:
            raise ValueError("delay must be at least one tick")


@dataclass(order=True)
class Event:
    tick: int
    sequence: int
    target: int = field(compare=False)
    amplitude: float = field(compare=False)


@dataclass
class EnergyCluster:
    energy: float
    neuron_ids: tuple[int, ...]

    def __post_init__(self):
        if not math.isfinite(self.energy) or self.energy < 0:
            raise ValueError("cluster energy must be finite and non-negative")


class SNNEngine:
    """Fixed-slot SNN whose scheduler visits only event-addressed neurons.

    Membrane leakage is applied lazily when a neuron next receives an event.
    The event queue, rather than the full neuron/synapse population, drives each
    scheduler tick. This is a CPU reference implementation, not a claim of
    physical per-neuron power gating.
    """

    def __init__(
        self,
        neurons: List[Neuron],
        synapses: List[Synapse],
        clusters: List[EnergyCluster],
        energy_per_spike: float = 0.01,
        refractory_ticks: int = 1,
    ):
        if not math.isfinite(energy_per_spike) or energy_per_spike < 0:
            raise ValueError("energy_per_spike must be finite and non-negative")
        if refractory_ticks < 0:
            raise ValueError("refractory_ticks must be non-negative")

        self.neurons, self.synapses, self.clusters = neurons[:], synapses[:], clusters[:]
        self.energy_per_spike = energy_per_spike
        self.refractory_ticks = refractory_ticks
        self.tick, self._sequence, self._queue = 0, 0, []
        self._cluster_for_neuron: dict[int, int] = {}
        self._outgoing_synapses: dict[int, list[int]] = {}

        for ci, cluster in enumerate(self.clusters):
            for nid in cluster.neuron_ids:
                self._check_neuron_id(nid)
                if nid in self._cluster_for_neuron:
                    raise ValueError("neuron belongs to multiple energy clusters")
                self._cluster_for_neuron[nid] = ci

        for synapse_id, syn in enumerate(self.synapses):
            self._check_neuron_id(syn.source)
            self._check_neuron_id(syn.target)
            self._outgoing_synapses.setdefault(syn.source, []).append(synapse_id)

    def _check_neuron_id(self, nid):
        if nid < 0 or nid >= len(self.neurons):
            raise ValueError("unknown neuron")

    def inject(self, neuron_id: int, amplitude: float, at_tick: Optional[int] = None):
        self._check_neuron_id(neuron_id)
        if not math.isfinite(amplitude):
            raise ValueError("event amplitude must be finite")
        target_tick = self.tick if at_tick is None else at_tick
        if target_tick < self.tick:
            raise ValueError("cannot schedule event in the past")
        self._sequence += 1
        heapq.heappush(
            self._queue,
            Event(target_tick, self._sequence, neuron_id, amplitude),
        )

    def replenish(self, cluster_id: int, amount: float):
        if cluster_id < 0 or cluster_id >= len(self.clusters):
            raise IndexError("unknown energy cluster")
        if not math.isfinite(amount) or amount < 0:
            raise ValueError("replenishment must be finite and non-negative")
        cluster = self.clusters[cluster_id]
        cluster.energy += amount
        # Re-evaluate only members of the replenished local energy cluster.
        for neuron_id in cluster.neuron_ids:
            if self.neurons[neuron_id].alive:
                self.inject(neuron_id, 0.0)

    def _apply_event(self, event: Event) -> bool:
        neuron = self.neurons[event.target]
        if not neuron.alive:
            return False

        elapsed = self.tick - neuron.last_update_tick
        if elapsed > 0:
            neuron.membrane *= neuron.leak ** elapsed
        neuron.last_update_tick = self.tick
        neuron.membrane += event.amplitude
        return True

    def step(self) -> list[int]:
        """Advance one tick; evaluate only neurons addressed by due events."""
        due_events = []
        while self._queue and self._queue[0].tick <= self.tick:
            due_events.append(heapq.heappop(self._queue))

        if not due_events:
            self.tick += 1
            return []

        touched = set()
        for event in due_events:
            if self._apply_event(event):
                touched.add(event.target)

        fired = []
        for neuron_id in sorted(touched):
            neuron = self.neurons[neuron_id]
            if not neuron.alive:
                continue

            if self.tick < neuron.refractory_until:
                if neuron.membrane >= neuron.threshold:
                    self.inject(neuron_id, 0.0, at_tick=neuron.refractory_until)
                continue

            if neuron.membrane < neuron.threshold:
                continue

            cluster_id = self._cluster_for_neuron.get(neuron_id)
            if cluster_id is None:
                continue
            cluster = self.clusters[cluster_id]
            if cluster.energy < self.energy_per_spike:
                continue

            cluster.energy -= self.energy_per_spike
            neuron.membrane = 0.0
            neuron.refractory_until = self.tick + self.refractory_ticks + 1
            neuron.spikes += 1
            fired.append(neuron_id)

            # Adjacency lookup avoids scanning unrelated synapses.
            for synapse_id in self._outgoing_synapses.get(neuron_id, ()):
                synapse = self.synapses[synapse_id]
                if synapse.active:
                    self.inject(
                        synapse.target,
                        synapse.weight,
                        self.tick + synapse.delay,
                    )

        self.tick += 1
        return fired

    def tombstone_neuron(self, neuron_id: int):
        """Deactivate a fixed slot without moving any other neuron."""
        self._check_neuron_id(neuron_id)
        self.neurons[neuron_id].alive = False
        self.neurons[neuron_id].membrane = 0.0
        for synapse in self.synapses:
            if synapse.source == neuron_id or synapse.target == neuron_id:
                synapse.active = False

    def update_hamiltonian_synapse(
        self,
        synapse_id: int,
        dt: float,
        stiffness: float = 1.0,
    ) -> float:
        """Velocity-Verlet step for H=0.5*P^2+0.5*k*W^2."""
        if synapse_id < 0 or synapse_id >= len(self.synapses):
            raise IndexError("unknown synapse")
        if not math.isfinite(dt) or dt <= 0:
            raise ValueError("dt must be finite and positive")
        if not math.isfinite(stiffness) or stiffness <= 0:
            raise ValueError("stiffness must be finite and positive")
        synapse = self.synapses[synapse_id]
        energy = lambda: 0.5 * synapse.momentum**2 + 0.5 * stiffness * synapse.weight**2
        if synapse.invariant:
            return energy()
        p_half = synapse.momentum - 0.5 * dt * stiffness * synapse.weight
        synapse.weight += dt * p_half
        synapse.momentum = p_half - 0.5 * dt * stiffness * synapse.weight
        return energy()

    def mark_stable_invariants(self, variance_epsilon: float = 1e-8) -> list[int]:
        """Prototype only: single-sample stability is not production evidence."""
        if variance_epsilon < 0 or not math.isfinite(variance_epsilon):
            raise ValueError("invalid epsilon")
        frozen = []
        for synapse_id, synapse in enumerate(self.synapses):
            if not synapse.active:
                continue
            synapse.stable_cycles = (
                synapse.stable_cycles + 1
                if abs(synapse.momentum) <= variance_epsilon
                else 0
            )
            if synapse.stable_cycles >= 3:
                synapse.invariant = True
                frozen.append(synapse_id)
        return frozen
