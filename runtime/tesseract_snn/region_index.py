"""Compact multidimensional region index; stores locators, never source payloads."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Iterable


def _token(value: str, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}_REQUIRED")
    return value.strip().casefold()


@dataclass(frozen=True)
class RegionDescriptor:
    """One independently addressable region within a canonical source revision."""

    source_ref: str
    region_ref: str
    facets: Mapping[str, tuple[str, ...]]
    relations: tuple[str, ...] = ()

    def __post_init__(self):
        _token(self.source_ref, "SOURCE_REF")
        _token(self.region_ref, "REGION_REF")
        if not isinstance(self.facets, Mapping):
            raise ValueError("FACETS_MAPPING_REQUIRED")
        for dimension, values in self.facets.items():
            _token(dimension, "FACET_DIMENSION")
            if not isinstance(values, (tuple, list)) or not values:
                raise ValueError("FACET_VALUES_REQUIRED")
            for value in values:
                _token(value, "FACET_VALUE")
        if not isinstance(self.relations, (tuple, list)):
            raise ValueError("RELATIONS_SEQUENCE_REQUIRED")
        for relation in self.relations:
            _token(relation, "RELATION_REF")


class RegionIndex:
    """In-memory locator index with inverted facet and relation indexes.

    Registering descriptors does not open or load their source files. Callers
    resolve a returned source_ref/region_ref only after policy admission.
    """

    def __init__(self, descriptors: Iterable[RegionDescriptor] = ()):
        self._regions: dict[str, RegionDescriptor] = {}
        self._facet_postings: dict[tuple[str, str], set[str]] = {}
        self._outgoing: dict[str, set[str]] = {}
        self._incoming: dict[str, set[str]] = {}
        for descriptor in descriptors:
            self.add(descriptor)

    def add(self, descriptor: RegionDescriptor) -> None:
        if not isinstance(descriptor, RegionDescriptor):
            raise TypeError("REGION_DESCRIPTOR_REQUIRED")
        region_id = _token(descriptor.region_ref, "REGION_REF")
        if region_id in self._regions:
            raise ValueError(f"DUPLICATE_REGION_REF:{descriptor.region_ref}")
        self._regions[region_id] = descriptor
        for dimension, values in descriptor.facets.items():
            dim = _token(dimension, "FACET_DIMENSION")
            for value in values:
                key = (dim, _token(value, "FACET_VALUE"))
                self._facet_postings.setdefault(key, set()).add(region_id)
        for target in descriptor.relations:
            target_id = _token(target, "RELATION_REF")
            self._outgoing.setdefault(region_id, set()).add(target_id)
            self._incoming.setdefault(target_id, set()).add(region_id)

    def query(self, facets: Mapping[str, str], limit: int = 32) -> list[RegionDescriptor]:
        """Return bounded candidates matching every requested dimension/value."""
        if not isinstance(facets, Mapping):
            raise ValueError("FACET_QUERY_MAPPING_REQUIRED")
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
            raise ValueError("POSITIVE_QUERY_LIMIT_REQUIRED")
        if not facets:
            candidates = set(self._regions)
        else:
            postings = []
            for dimension, value in facets.items():
                key = (_token(dimension, "FACET_DIMENSION"),
                       _token(value, "FACET_VALUE"))
                posting = self._facet_postings.get(key)
                if not posting:
                    return []
                postings.append(posting)
            postings.sort(key=len)
            candidates = set(postings[0])
            for posting in postings[1:]:
                candidates.intersection_update(posting)
                if not candidates:
                    return []
        return [self._regions[key] for key in sorted(candidates)[:limit]]

    def related(self, region_ref: str, limit: int = 32) -> list[RegionDescriptor]:
        """Return known direct inbound/outbound neighbors without source reads."""
        region_id = _token(region_ref, "REGION_REF")
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
            raise ValueError("POSITIVE_QUERY_LIMIT_REQUIRED")
        neighbors = (self._outgoing.get(region_id, set()) |
                     self._incoming.get(region_id, set()))
        return [self._regions[key] for key in sorted(neighbors)
                if key in self._regions][:limit]

    def get(self, region_ref: str) -> RegionDescriptor | None:
        return self._regions.get(_token(region_ref, "REGION_REF"))

    def __len__(self) -> int:
        return len(self._regions)
