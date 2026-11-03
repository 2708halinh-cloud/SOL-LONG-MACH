"""Integrated TESSERACT motherboard cycle.

This is a software-defined local control plane. Provider sockets are metadata
adapters supplied by the host; this module never invents reachability,
authorization, credentials, or remote-provider success.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable, Mapping

from runtime.continuity_guard import (
    Checkpoint,
    continue_bounded,
    save_checkpoint,
    select_next_callable_edge,
    stop_allowed,
    visible_output_allowed,
)
from runtime.motherboard_control_plane import (
    AffectEvent,
    Blackboard,
    CpuSocket,
    DiskWriteGuard,
    gate1_preflight,
    gate2_readback,
    route_candidates,
)
from runtime.tesseract_snn.core import SNNEngine
from runtime.tesseract_snn.journal import AppendOnlyJournal


Executor = Callable[[CpuSocket, Any, str], Mapping[str, Any]]


class TesseractMotherboard:
    """Join CPU sockets, Gate 1/2, RAM_L1, PMIC, SNN and Core Journal.

    A cycle is bounded. OPEN remains an unfinished objective, not a stop
    instruction. The board reports the next executable edge or the exact
    unresolved dependency; it never converts a partial action into completion.
    """

    def __init__(
        self,
        *,
        sockets: list[CpuSocket],
        executors: Mapping[str, Executor],
        checkpoint_path: str | Path,
        journal_path: str | Path,
        disk_guard: DiskWriteGuard | None = None,
        blackboard: Blackboard | None = None,
        snn_engine: SNNEngine | None = None,
    ) -> None:
        ids = [socket.socket_id for socket in sockets]
        if len(ids) != len(set(ids)):
            raise ValueError("DUPLICATE_CPU_SOCKET_ID")
        self.sockets = {socket.socket_id: socket for socket in sockets}
        self.executors = dict(executors)
        self.checkpoint_path = Path(checkpoint_path)
        self.journal = AppendOnlyJournal(journal_path)
        self.disk_guard = disk_guard or DiskWriteGuard()
        self.blackboard = blackboard or Blackboard()
        self.snn_engine = snn_engine
        self._cycle = 0

    @staticmethod
    def _valid_refs(refs: object) -> bool:
        return (
            isinstance(refs, (list, tuple))
            and bool(refs)
            and all(isinstance(ref, str) and ref.strip() for ref in refs)
        )

    @staticmethod
    def _receipt_summary(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Persist identifiers only; never copy arbitrary provider payloads/secrets."""
        allowed = ("carrier", "receipt_id", "provider", "observed_at",
                   "action_kind", "error_code", "error_class", "retryable")
        summaries = []
        for receipt in receipts:
            if not isinstance(receipt, dict):
                continue
            item = {key: receipt[key] for key in allowed
                    if key in receipt and isinstance(receipt[key], (str, int, float, bool))}
            summaries.append(item)
        return summaries

    @staticmethod
    def _safe_result(raw: object, carrier: str) -> dict[str, Any]:
        if not isinstance(raw, Mapping):
            return {"success": False, "carrier": carrier, "error_code": "INVALID_EXECUTOR_RESULT"}

        def project(value: object, keys: tuple[str, ...]) -> dict[str, Any] | None:
            if not isinstance(value, Mapping):
                return None
            return {
                key: value[key]
                for key in keys
                if key in value and isinstance(value[key], (str, int, float, bool))
            }

        receipt = project(raw.get("provider_receipt"),
                          ("receipt_id", "provider", "observed_at", "source_ref"))
        consequence = project(raw.get("observable_consequence"),
                               ("changed", "target_ref", "consequence_ref", "observed_at"))
        readback = project(raw.get("readback"),
                           ("verified", "source", "sha256", "observed_at", "state_consistent"))
        result: dict[str, Any] = {
            "success": raw.get("success") is True,
            "carrier": carrier,
            "action_kind": raw.get("action_kind") if isinstance(raw.get("action_kind"), str) else "ACTION",
            "provider_receipt": receipt,
            "observable_consequence": consequence,
            "readback": readback,
            "state_consistent": raw.get("state_consistent") is True,
        }
        for key in ("last_consequence_ref", "error_code", "error_class"):
            if isinstance(raw.get(key), str):
                result[key] = raw[key]
        if isinstance(raw.get("retryable"), bool):
            result["retryable"] = raw["retryable"]
        return result

    def _refresh_routes(self, checkpoint: Checkpoint) -> None:
        for edge in checkpoint.edges:
            if edge.done or edge.user_input_required:
                continue
            capability = edge.evidence.get("capability")
            if not isinstance(capability, str) or not capability.strip():
                edge.callable_now = False
                edge.evidence["route_discovery_required"] = True
                continue

            candidates = route_candidates(list(self.sockets.values()), capability)
            for socket in candidates:
                if socket.socket_id not in edge.candidate_carriers:
                    edge.candidate_carriers.append(socket.socket_id)

            if edge.evidence.get("resource_guard_blocked") is True:
                if not self.disk_guard.permits_nonessential_writes:
                    edge.callable_now = False
                    continue
                edge.evidence.setdefault("resource_guard_events", []).append(
                    {"state": "REARMED_AFTER_PMIC_RECOVERY"}
                )
                edge.evidence["resource_guard_blocked"] = False

            if edge.next_carrier() is not None:
                edge.callable_now = True
            else:
                edge.callable_now = False
                edge.evidence["route_discovery_required"] = True

    def _apply_disk_sample(self, sample: Mapping[str, Any] | None) -> str:
        if not isinstance(sample, Mapping):
            return self.disk_guard.observe(None, None, sample_fresh=False)
        return self.disk_guard.observe(
            sample.get("total_bytes"),
            sample.get("free_bytes"),
            sample_fresh=sample.get("sample_fresh") is True,
        )

    def _executor(self, edge: Any, carrier: str | None) -> dict[str, Any]:
        if carrier is None:
            return {"success": False, "error_code": "NO_PROVIDER_CARRIER"}
        socket = self.sockets.get(carrier)
        capability = edge.evidence.get("capability")
        if socket is None or not isinstance(capability, str) or not socket.can_run(capability):
            return {"success": False, "carrier": carrier, "error_code": "SOCKET_NOT_READY"}

        evidence = edge.evidence
        gate1 = gate1_preflight(
            authorized=socket.authorized and evidence.get("authorized") is True,
            target_identity_verified=evidence.get("target_identity_verified") is True,
            policy_allowed=evidence.get("policy_allowed") is True,
            quota_available=socket.quota_available,
            destructive_change=evidence.get("destructive_change") is True,
            protected_target=evidence.get("protected_target") is True,
            explicit_approval=evidence.get("explicit_approval") is True,
        )
        if not gate1.allowed:
            return {
                "success": False,
                "carrier": carrier,
                "error_code": "GATE1_DENIED",
                "gate1_reasons": list(gate1.reasons),
            }

        provider = self.executors.get(carrier)
        if not callable(provider):
            return {"success": False, "carrier": carrier, "error_code": "EXECUTOR_NOT_REGISTERED"}

        try:
            raw = provider(socket, edge, carrier)
        except Exception as exc:
            # Keep exception text out of durable records; it may contain secrets.
            return {
                "success": False,
                "carrier": carrier,
                "error_code": "PROVIDER_EXCEPTION",
                "error_class": type(exc).__name__,
                "retryable": True,
            }

        result = self._safe_result(raw, carrier)
        if result.get("success") is not True:
            return result

        readback = result.get("readback") or {}
        gate2 = gate2_readback(
            action_receipt=result.get("provider_receipt") is not None,
            consequence_observed=result.get("observable_consequence") is not None,
            independent_readback=readback.get("verified") is True,
            state_consistent=result.get("state_consistent") is True,
        )
        if not gate2.allowed:
            result["success"] = False
            result["error_code"] = "GATE2_READBACK_DENIED"
            result["gate2_reasons"] = list(gate2.reasons)
        return result

    def _write_blocked_edges(self, checkpoint: Checkpoint) -> None:
        for edge in checkpoint.edges:
            if edge.done or edge.user_input_required:
                continue
            if edge.evidence.get("write_required") is True and not self.disk_guard.permits_nonessential_writes:
                edge.callable_now = False
                edge.evidence["resource_guard_blocked"] = True
                edge.evidence.setdefault("resource_guard_events", []).append(
                    {"state": "BLOCKED_NONESSENTIAL_WRITE", "level": self.disk_guard.level}
                )

    def _state(self, checkpoint: Checkpoint) -> str:
        if checkpoint.objective_done():
            return "OBJECTIVE_DONE"
        if select_next_callable_edge(checkpoint) is not None:
            return "OPEN_CONTINUE"
        if checkpoint.user_dependencies():
            return "OPEN_USER_INPUT_REQUIRED"
        return "OPEN_ROUTE_DISCOVERY_REQUIRED"

    def _blackboard_readback(
        self,
        checkpoint: Checkpoint,
        state: str,
        source_refs: list[str],
        history_refs: list[str],
        affect: AffectEvent | None,
        receipts: list[dict[str, Any]],
    ) -> None:
        updates = (
            ("REG_00", {
                "objective_id": checkpoint.objective_id,
                "source_marker": checkpoint.source_marker,
                "lineage_ref": checkpoint.lineage_ref,
                "source_refs": list(source_refs),
                "history_refs": list(history_refs),
                "state_n": checkpoint.state_n,
            }),
            ("REG_01", {
                "last_cycle": self._cycle,
                "receipt_summaries": self._receipt_summary(receipts),
            }),
            ("REG_02", {
                "signal": affect.signal if affect else None,
                "context": affect.context if affect else None,
                "observed_facts": list(affect.observed_facts) if affect else [],
                "cause_hypotheses": list(affect.cause_hypotheses) if affect else [],
            }),
            ("REG_03", {
                "state": state,
                "open_edges": [e.edge_id for e in checkpoint.unfinished_edges()],
                "next_edge": (
                    select_next_callable_edge(checkpoint).edge_id
                    if select_next_callable_edge(checkpoint) else None
                ),
                "disk_guard": self.disk_guard.level,
                "stop_allowed": stop_allowed(checkpoint),
            }),
        )
        for register, payload in updates:
            self.blackboard.update(register, payload, expected_version=self.blackboard.version)
        for register, _ in updates:
            if self.blackboard.registers.get(register) is None:
                raise RuntimeError("BLACKBOARD_READBACK_MISSING")

    def run_cycle(
        self,
        checkpoint: Checkpoint,
        *,
        source_refs: list[str],
        history_refs: list[str],
        disk_sample: Mapping[str, Any] | None = None,
        affect: AffectEvent | None = None,
        max_steps: int = 32,
    ) -> dict[str, Any]:
        if not isinstance(checkpoint, Checkpoint):
            raise TypeError("checkpoint must be a continuity_guard.Checkpoint")
        if not isinstance(max_steps, int) or max_steps < 0:
            raise ValueError("max_steps must be a non-negative integer")

        self._cycle += 1
        disk_level = self._apply_disk_sample(disk_sample)
        if self.snn_engine is not None and self.snn_engine.neurons:
            self.snn_engine.inject(0, 1.0)
            snn_spikes = self.snn_engine.step()
        else:
            snn_spikes = []

        if not self._valid_refs(source_refs) or not self._valid_refs(history_refs):
            state = "OPEN_SOURCE_REVIEW"
            execution = {"steps": 0, "receipts": [], "objective_done": False}
            save_checkpoint(self.checkpoint_path, checkpoint)
            self._blackboard_readback(checkpoint, state, source_refs or [],
                                      history_refs or [], affect, [])
            record = self.journal.append({
                "kind": "TESSERACT_MAINBOARD_CYCLE",
                "cycle": self._cycle,
                "objective_id": checkpoint.objective_id,
                "state": state,
                "reason": "SOURCE_OR_HISTORY_ANCHOR_MISSING",
                "checkpoint_sha256": sha256(self.checkpoint_path.read_bytes()).hexdigest(),
            })
            return {
                "state": state,
                "steps": 0,
                "objective_done": False,
                "completion_allowed": False,
                "next_edge": None,
                "disk_guard": disk_level,
                "snn_spikes": snn_spikes,
                "journal_verified": self.journal.verify(),
                "journal_record_hash": record["record_hash"],
            }

        self._refresh_routes(checkpoint)
        self._write_blocked_edges(checkpoint)
        execution = continue_bounded(checkpoint, self._executor, max_steps=max_steps)
        state = self._state(checkpoint)
        save_checkpoint(self.checkpoint_path, checkpoint)
        self._blackboard_readback(
            checkpoint, state, source_refs, history_refs, affect,
            execution.get("receipts", []),
        )
        checkpoint_hash = sha256(self.checkpoint_path.read_bytes()).hexdigest()
        record = self.journal.append({
            "kind": "TESSERACT_MAINBOARD_CYCLE",
            "cycle": self._cycle,
            "objective_id": checkpoint.objective_id,
            "source_marker": checkpoint.source_marker,
            "lineage_ref": checkpoint.lineage_ref,
            "source_refs": list(source_refs),
            "history_refs": list(history_refs),
            "state": state,
            "steps": execution.get("steps", 0),
            "objective_done": checkpoint.objective_done(),
            "open_edges": [e.edge_id for e in checkpoint.unfinished_edges()],
            "receipt_summaries": self._receipt_summary(execution.get("receipts", [])),
            "disk_guard": disk_level,
            "checkpoint_sha256": checkpoint_hash,
            "snn_spikes": list(snn_spikes),
        })
        return {
            "state": state,
            "steps": execution.get("steps", 0),
            "objective_done": checkpoint.objective_done(),
            "completion_allowed": visible_output_allowed(checkpoint, output_kind="COMPLETION"),
            "report_allowed": visible_output_allowed(checkpoint, output_kind="REPORT"),
            "stop_allowed": stop_allowed(checkpoint),
            "next_edge": (
                select_next_callable_edge(checkpoint).edge_id
                if select_next_callable_edge(checkpoint) else None
            ),
            "open_edges": [e.edge_id for e in checkpoint.unfinished_edges()],
            "disk_guard": disk_level,
            "snn_spikes": snn_spikes,
            "journal_verified": self.journal.verify(),
            "journal_record_hash": record["record_hash"],
            "checkpoint_sha256": checkpoint_hash,
            "blackboard_version": self.blackboard.version,
        }
