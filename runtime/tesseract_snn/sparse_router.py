"""Sparse routing from multidimensional source regions into the SNN event queue."""
from __future__ import annotations

import math
from typing import Mapping

from .core import SNNEngine
from .region_index import RegionDescriptor, RegionIndex


class SparseRegionRouter:
    """Resolve bounded region candidates and stimulate only mapped neurons.

    This component does not load source payloads or invoke external tools.
    It emits neural events only. A separate capability gateway must resolve
    adapter schemas, permissions, approvals, arguments and side effects.
    """

    def __init__(
        self,
        region_index: RegionIndex,
        engine: SNNEngine,
        neuron_by_region: Mapping[str, int],
    ):
        if not isinstance(region_index, RegionIndex):
            raise TypeError("REGION_INDEX_REQUIRED")
        if not isinstance(engine, SNNEngine):
            raise TypeError("SNN_ENGINE_REQUIRED")
        if not isinstance(neuron_by_region, Mapping):
            raise TypeError("NEURON_MAPPING_REQUIRED")
        self.region_index = region_index
        self.engine = engine
        self._neuron_by_region = {}
        self._region_by_neuron = {}
        for region_ref, neuron_id in neuron_by_region.items():
            descriptor = region_index.get(region_ref)
            if descriptor is None:
                raise KeyError(f"UNINDEXED_REGION:{region_ref}")
            engine._check_neuron_id(neuron_id)
            if neuron_id in self._region_by_neuron:
                raise ValueError(f"DUPLICATE_NEURON_BINDING:{neuron_id}")
            key = region_ref.strip().casefold()
            self._neuron_by_region[key] = neuron_id
            self._region_by_neuron[neuron_id] = descriptor.region_ref

    def route(
        self,
        facets: Mapping[str, str],
        stimulus: float = 1.0,
        limit: int = 32,
    ) -> list[RegionDescriptor]:
        if not math.isfinite(stimulus) or stimulus <= 0:
            raise ValueError("STIMULUS_MUST_BE_FINITE_AND_POSITIVE")
        candidates = self.region_index.query(facets, limit=limit)
        # Validate the whole bounded set before mutating the event queue.
        bindings = []
        for descriptor in candidates:
            key = descriptor.region_ref.strip().casefold()
            neuron_id = self._neuron_by_region.get(key)
            if neuron_id is None:
                raise KeyError(f"UNBOUND_REGION:{descriptor.region_ref}")
            bindings.append(neuron_id)
        for neuron_id in bindings:
            self.engine.inject(neuron_id, stimulus)
        return candidates

    def fired_regions(self, neuron_ids: list[int]) -> list[str]:
        """Translate fired neuron slots back to exact source-region references."""
        regions = []
        for neuron_id in neuron_ids:
            region_ref = self._region_by_neuron.get(neuron_id)
            if region_ref is not None:
                regions.append(region_ref)
        return regions
