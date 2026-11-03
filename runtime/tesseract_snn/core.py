"""Deterministic CPU reference engine for TESSERACT's event-driven SNN prototype."""
from __future__ import annotations
from dataclasses import dataclass, field
import heapq, math
from typing import List, Optional

@dataclass
class Neuron:
    threshold: float = 1.0
    leak: float = 0.95
    membrane: float = 0.0
    refractory_until: int = 0
    alive: bool = True
    spikes: int = 0
    def __post_init__(self):
        if not math.isfinite(self.threshold) or self.threshold <= 0: raise ValueError("threshold must be finite and positive")
        if not math.isfinite(self.leak) or not 0 <= self.leak <= 1: raise ValueError("leak must be in [0, 1]")

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
        if not math.isfinite(self.weight) or not math.isfinite(self.momentum): raise ValueError("synapse state must be finite")
        if self.delay < 1: raise ValueError("delay must be at least one tick")

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
        if not math.isfinite(self.energy) or self.energy < 0: raise ValueError("cluster energy must be finite and non-negative")

class SNNEngine:
    """Fixed-slot event-driven SNN with local energy pools and phase state."""
    def __init__(self, neurons: List[Neuron], synapses: List[Synapse], clusters: List[EnergyCluster], energy_per_spike: float = 0.01, refractory_ticks: int = 1):
        if not math.isfinite(energy_per_spike) or energy_per_spike < 0: raise ValueError("energy_per_spike must be finite and non-negative")
        if refractory_ticks < 0: raise ValueError("refractory_ticks must be non-negative")
        self.neurons, self.synapses, self.clusters = neurons[:], synapses[:], clusters[:]
        self.energy_per_spike, self.refractory_ticks = energy_per_spike, refractory_ticks
        self.tick, self._sequence, self._queue = 0, 0, []
        self._cluster_for_neuron = {}
        for ci, cluster in enumerate(self.clusters):
            for nid in cluster.neuron_ids:
                self._check_neuron_id(nid)
                if nid in self._cluster_for_neuron: raise ValueError("neuron belongs to multiple energy clusters")
                self._cluster_for_neuron[nid] = ci
        for syn in self.synapses:
            self._check_neuron_id(syn.source); self._check_neuron_id(syn.target)
    def _check_neuron_id(self, nid):
        if nid < 0 or nid >= len(self.neurons): raise ValueError("unknown neuron")
    def inject(self, neuron_id: int, amplitude: float, at_tick: Optional[int] = None):
        self._check_neuron_id(neuron_id)
        if not math.isfinite(amplitude): raise ValueError("event amplitude must be finite")
        target_tick = self.tick if at_tick is None else at_tick
        if target_tick < self.tick: raise ValueError("cannot schedule event in the past")
        self._sequence += 1
        heapq.heappush(self._queue, Event(target_tick, self._sequence, neuron_id, amplitude))
    def replenish(self, cluster_id: int, amount: float):
        if cluster_id < 0 or cluster_id >= len(self.clusters): raise IndexError("unknown energy cluster")
        if not math.isfinite(amount) or amount < 0: raise ValueError("replenishment must be finite and non-negative")
        self.clusters[cluster_id].energy += amount
    def step(self) -> list[int]:
        """Advance one event tick and return neuron IDs that emitted spikes."""
        due = []
        while self._queue and self._queue[0].tick <= self.tick: due.append(heapq.heappop(self._queue))
        for event in due:
            neuron = self.neurons[event.target]
            if neuron.alive: neuron.membrane += event.amplitude
        fired = []
        for nid, neuron in enumerate(self.neurons):
            if not neuron.alive: continue
            neuron.membrane *= neuron.leak
            if self.tick < neuron.refractory_until or neuron.membrane < neuron.threshold: continue
            ci = self._cluster_for_neuron.get(nid)
            if ci is None or self.clusters[ci].energy < self.energy_per_spike: continue
            self.clusters[ci].energy -= self.energy_per_spike
            neuron.membrane, neuron.refractory_until = 0.0, self.tick + self.refractory_ticks + 1
            neuron.spikes += 1; fired.append(nid)
            for syn in self.synapses:
                if syn.active and syn.source == nid: self.inject(syn.target, syn.weight, self.tick + syn.delay)
        self.tick += 1
        return fired
    def tombstone_neuron(self, neuron_id: int):
        """Deactivate a fixed slot without moving any other neuron."""
        self._check_neuron_id(neuron_id)
        self.neurons[neuron_id].alive = False
        self.neurons[neuron_id].membrane = 0.0
        for syn in self.synapses:
            if syn.source == neuron_id or syn.target == neuron_id: syn.active = False
    def update_hamiltonian_synapse(self, synapse_id: int, dt: float, stiffness: float = 1.0) -> float:
        """Velocity-Verlet step for H=0.5*P^2+0.5*k*W^2."""
        if synapse_id < 0 or synapse_id >= len(self.synapses): raise IndexError("unknown synapse")
        if not math.isfinite(dt) or dt <= 0: raise ValueError("dt must be finite and positive")
        if not math.isfinite(stiffness) or stiffness <= 0: raise ValueError("stiffness must be finite and positive")
        syn = self.synapses[synapse_id]
        energy = lambda: 0.5 * syn.momentum**2 + 0.5 * stiffness * syn.weight**2
        if syn.invariant: return energy()
        p_half = syn.momentum - 0.5 * dt * stiffness * syn.weight
        syn.weight += dt * p_half
        syn.momentum = p_half - 0.5 * dt * stiffness * syn.weight
        return energy()
    def mark_stable_invariants(self, variance_epsilon: float = 1e-8) -> list[int]:
        """Prototype only: single-sample stability is not production evidence."""
        if variance_epsilon < 0 or not math.isfinite(variance_epsilon): raise ValueError("invalid epsilon")
        frozen = []
        for i, syn in enumerate(self.synapses):
            if not syn.active: continue
            syn.stable_cycles = syn.stable_cycles + 1 if abs(syn.momentum) <= variance_epsilon else 0
            if syn.stable_cycles >= 3: syn.invariant = True; frozen.append(i)
        return frozen
