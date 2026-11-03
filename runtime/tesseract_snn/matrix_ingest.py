"""Source-bound parser and runtime builder for the canonical ITEM matrix.

The importer indexes explicit item boundaries and explicit RELATED_ITEMS only.
It does not summarize, rewrite, infer semantic relations, or copy item bodies
into the runtime index.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping

from .core import EnergyCluster, Neuron, SNNEngine
from .region_index import RegionDescriptor, RegionIndex
from .sparse_router import SparseRegionRouter


_ITEM_MARKER = re.compile(
    r"<!-- BEGIN_ITEM_(R-\d{3}) -->\s*(.*?)\s*<!-- END_ITEM_\1 -->",
    re.DOTALL,
)
_BEGIN_MARKER = re.compile(r"<!-- BEGIN_ITEM_(R-\d{3}) -->")
_END_MARKER = re.compile(r"<!-- END_ITEM_(R-\d{3}) -->")
_RELATED = re.compile(r"^\s*RELATED_ITEMS\s*:\s*(.*?)\s*$", re.MULTILINE)
_ITEM_REF = re.compile(r"R-\d{3}")


@dataclass(frozen=True)
class MatrixRuntime:
    region_index: RegionIndex
    engine: SNNEngine
    router: SparseRegionRouter
    neuron_by_item: Mapping[str, int]
    source_ref: str


def parse_item_matrix(
    markdown: str,
    *,
    source_uri: str,
    source_revision: str,
    revision_kind: str,
) -> list[RegionDescriptor]:
    """Parse explicit source boundaries into locator-only region descriptors."""
    if not isinstance(markdown, str) or not markdown.strip():
        raise ValueError("MATRIX_SOURCE_REQUIRED")
    if not isinstance(source_uri, str) or not source_uri.strip():
        raise ValueError("SOURCE_URI_REQUIRED")
    if not isinstance(source_revision, str) or not re.fullmatch(r"[0-9a-fA-F]{7,64}", source_revision):
        raise ValueError("SOURCE_REVISION_REQUIRED")
    if revision_kind not in {"git-blob-sha1", "git-commit-sha1", "sha256", "version-id"}:
        raise ValueError("SUPPORTED_REVISION_KIND_REQUIRED")

    begins = list(_BEGIN_MARKER.finditer(markdown))
    ends = list(_END_MARKER.finditer(markdown))
    matches = list(_ITEM_MARKER.finditer(markdown))
    if not begins or len(begins) != len(ends) or len(matches) != len(begins):
        raise ValueError("ITEM_BOUNDARY_MISMATCH")

    source_ref = f"{source_uri.strip()}@{revision_kind}:{source_revision.lower()}"
    seen: set[str] = set()
    descriptors: list[RegionDescriptor] = []
    for match in matches:
        item_id, body = match.group(1), match.group(2)
        if item_id in seen:
            raise ValueError(f"DUPLICATE_ITEM:{item_id}")
        seen.add(item_id)

        title_match = re.search(r"^\s*#\s+(.+?)\s*$", body, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else item_id

        related: list[str] = []
        for relation_line in _RELATED.findall(body):
            related.extend(_ITEM_REF.findall(relation_line))
        related = list(dict.fromkeys(related))

        descriptors.append(
            RegionDescriptor(
                source_ref=source_ref,
                region_ref=f"{source_ref}#{item_id}",
                facets={"item_id": (item_id,), "title": (title,)},
                relations=tuple(related),
            )
        )

    return descriptors


def build_matrix_runtime(
    markdown: str,
    *,
    source_uri: str,
    source_revision: str,
    revision_kind: str,
    initial_energy: float,
    energy_per_spike: float = 0.01,
) -> MatrixRuntime:
    """Create a CPU reference runtime with stable slots in source order.

    initial_energy is a simulation budget, not measured hardware energy and
    not a claim about physical power gating.
    """
    descriptors = parse_item_matrix(
        markdown,
        source_uri=source_uri,
        source_revision=source_revision,
        revision_kind=revision_kind,
    )
    if not isinstance(initial_energy, (int, float)) or isinstance(initial_energy, bool) or not re.fullmatch(r"(?:0|[1-9]\d*)(?:\.\d+)?", str(initial_energy)):
        raise ValueError("INITIAL_ENERGY_MUST_BE_NON_NEGATIVE")
    if initial_energy < 0:
        raise ValueError("INITIAL_ENERGY_MUST_BE_NON_NEGATIVE")

    neuron_by_item = {
        descriptor.facets["item_id"][0]: slot
        for slot, descriptor in enumerate(descriptors)
    }
    neurons = [Neuron(threshold=1.0, leak=0.95) for _ in descriptors]
    engine = SNNEngine(
        neurons=neurons,
        synapses=[],
        clusters=[EnergyCluster(
            energy=float(initial_energy),
            neuron_ids=tuple(range(len(neurons))),
        )],
        energy_per_spike=energy_per_spike,
    )
    index = RegionIndex(descriptors)
    router = SparseRegionRouter(
        index,
        engine,
        {
            descriptor.region_ref: neuron_by_item[descriptor.facets["item_id"][0]]
            for descriptor in descriptors
        },
    )
    return MatrixRuntime(index, engine, router, neuron_by_item, descriptors[0].source_ref)
