"""Source-bound signal re-entry adapter over the durable continuity checkpoint.

This module does not claim perpetual background execution. Each invocation
restores a checkpoint, runs at most max_steps, and persists the unfinished tail.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from os import PathLike
from typing import Any, Callable

from runtime.continuity_guard import (
    Checkpoint,
    Edge,
    continue_bounded,
    load_checkpoint,
    save_checkpoint,
    select_next_callable_edge,
)


def verified_readback(readback: object) -> bool:
    """Require an explicit positive readback and a source-hash reference."""
    if not isinstance(readback, Mapping):
        return False
    source_hash = readback.get("source_hash")
    return (
        readback.get("verified") is True
        and isinstance(source_hash, str)
        and source_hash.startswith("sha256:")
        and len(source_hash) > len("sha256:")
    )


def signal_reentry(
    checkpoint_path: str | PathLike[str],
    *,
    signal_id: str,
    objective_id: str,
    source_marker: str,
    lineage_ref: str,
    incoming_edges: Iterable[Edge] = (),
    executor: Callable[[Edge, str | None], dict[str, Any]] | None = None,
    max_steps: int = 32,
) -> dict[str, Any]:
    """Restore one objective and continue only its still-callable edges."""
    identity = (signal_id, objective_id, source_marker, lineage_ref)
    if any(not isinstance(value, str) or not value.strip() for value in identity):
        raise ValueError("SIGNAL_REENTRY_REQUIRES_SOURCE_IDENTITY")
    if not isinstance(max_steps, int) or max_steps < 0:
        raise ValueError("max_steps must be a non-negative integer")

    new_edges = list(incoming_edges)
    if any(not isinstance(edge, Edge) for edge in new_edges):
        raise TypeError("incoming_edges must contain continuity_guard.Edge values")

    checkpoint = load_checkpoint(checkpoint_path)
    if checkpoint is None:
        checkpoint = Checkpoint(
            objective_id=objective_id,
            source_marker=source_marker,
            lineage_ref=lineage_ref,
            edges=new_edges,
        )
    else:
        if (
            checkpoint.objective_id != objective_id
            or checkpoint.source_marker != source_marker
            or checkpoint.lineage_ref != lineage_ref
        ):
            raise ValueError("SOURCE_IDENTITY_CONFLICT")

        existing = {edge.edge_id: edge for edge in checkpoint.edges}
        for edge in new_edges:
            prior = existing.get(edge.edge_id)
            if prior is not None:
                if prior.target != edge.target:
                    raise ValueError("EDGE_IDENTITY_CONFLICT")
                continue
            checkpoint.edges.append(edge)
            existing[edge.edge_id] = edge

    execution: dict[str, Any] = {}
    if executor is None:
        save_checkpoint(checkpoint_path, checkpoint)
    else:
        try:
            execution = continue_bounded(checkpoint, executor, max_steps=max_steps)
        finally:
            save_checkpoint(checkpoint_path, checkpoint)

    next_edge = select_next_callable_edge(checkpoint)
    unfinished = [edge.edge_id for edge in checkpoint.unfinished_edges()]
    if checkpoint.objective_done():
        state = "OBJECTIVE_DONE"
    elif executor is None:
        state = "SAVED_UNFINISHED_NO_EXECUTOR"
    elif checkpoint.user_dependencies():
        state = "USER_INPUT_REQUIRED"
    elif next_edge is not None:
        state = "CONTINUE_REQUIRED"
    else:
        state = "SAVED_UNFINISHED_NO_EXECUTOR"

    return {
        "state": state,
        "signal_id": signal_id,
        "objective_id": checkpoint.objective_id,
        "unfinished_edge_ids": unfinished,
        "next_action": next_edge.edge_id if next_edge is not None else None,
        "objective_done": checkpoint.objective_done(),
        "steps": execution.get("steps", 0),
        "receipts": execution.get("receipts", []),
    }
