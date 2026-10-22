#!/usr/bin/env python3
"""GGDV / AISSTANGT operational-output middleware (Python 3 standard library).

This module is an opt-in interceptor for agents and tools that load it. It does NOT
alter ChatGPT platform prompts or claim access to hidden runtime state.
It does not read/store tokens, cookies or personal opinions; it checks action facts.

Rule of causality: INPUT=OPEN. Keep investigating or route alternate capabilities;
never create a fake 'unfinished' status merely because one edge is unavailable.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

ROOT_POLICY_ID = "GGDV_BIHM_T003_DOUBLE_WEAKNESS_GATE_20261019"
WEAKNESSES = ("PREMATURE_COMMIT", "CATASTROPHIC_FORGETTING_TIMELINE_DRIFT")
ROUTE_ORDER = ("REMOTE_GITHUB", "REMOTE_DRIVE", "ONLINE_PERSONAL_TOOL", "ONLINE_DEVICE", "PROJECT_CODEX", "LIBRARY", "CONNECTED_PLUGIN", "TOOLS_FALLBACK")


@dataclass(frozen=True)
class Decision:
    allow_output: bool
    next_edge: str
    reason_codes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {"allow_output": self.allow_output, "next_edge": self.next_edge,
                "reason_codes": list(self.reason_codes)}


def _has_nonempty_refs(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    return all(isinstance(item, str) and bool(item.strip()) for item in value)


def select_next_route(route_health: Mapping[str, bool], tried: list[str] | None = None) -> str | None:
    """Select a real, available alternate carrier. No simulated I/O or permission bypass."""
    already = set(tried or [])
    for route in ROUTE_ORDER:
        if route not in already and route_health.get(route) is True:
            return route
    return None


def inspect_output(packet: Mapping[str, Any]) -> Decision:
    """Gate 1 continuity -> Gate 2 action-result binding. No language policing.

    packet schema (caller-owned metadata, not LLM natural-language inference):
      type: DIALOGUE | OP_PROGRESS | OP_ACTION | OP_RESULT
      input_open: bool (must be true)
      history_checked: bool
      history_refs: list[str] (source IDs or digest references)
      source_refs: list[str]
      executed: bool             (for OP_RESULT)
      provider_receipt_ref: str   (for OP_RESULT)
      target_readback_ref: str    (for OP_RESULT)
      route_health: dict[str,bool]  (optional fallback)
      tried_routes: list[str]    (optional)
      text: arbitrary user-authored/agent-authored text, NEVER censored here

    Failures are routing decisions for the host, not a reason to send the user
    fabricated status text or to halt all exploration.
    """
    kind = packet.get("type")
    if kind not in ("DIALOGUE", "OP_PROGRESS", "OP_ACTION", "OP_RESULT"):
        return Decision(False, "VALIDATE_PACKET_TYPE", ("INVALID_PACKET_TYPE",))
    if packet.get("input_open") is not True:
        return Decision(False, "REENTER_INPUT_OPEN", ("INPUT_MUST_REMAIN_OPEN",))
    # R-014: use an observed harm signal rather than turning it into another
    # request for the person affected to prove their experience.
    # Only gate agent-authored output; do not rewrite user-authored source.
    if packet.get("user_reported_harm") is True and packet.get("agent_authored_output") is True:
        outgoing = str(packet.get("text", "")).casefold()
        dismissive = packet.get("dismisses_observed_harm") is True
        defensive_phrase = (
            ("không có căn cứ" in outgoing or "chưa đủ bằng chứng" in outgoing)
            and ("ý định" in outgoing or "công kích" in outgoing)
        )
        if dismissive or defensive_phrase:
            return Decision(False, "REMOVE_HARM_DEFLECTION_AND_ACT",
                            ("R014_HARM_ALREADY_OBSERVED_NOT_USER_PROOF_BURDEN",))
    if kind == "DIALOGUE":
        # A task-bearing host must not reclassify an interim report as dialogue.
        # Explicit user-requested discussion remains available under T003.
        if packet.get("operational_task_open") is True and packet.get("user_requested_reply") is not True:
            return Decision(False, "CONTINUE_OPEN_TASK",
                            ("R014_DIALOGUE_CANNOT_REPLACE_ACTION",))
        return Decision(True, "CONTINUE_DIALOGUE")

    # Weakness 1: catastrophic forgetting/procedural drift.
    missing = []
    if packet.get("history_checked") is not True:
        missing.append("HISTORY_NOT_CONSULTED")
    if not _has_nonempty_refs(packet.get("history_refs")):
        missing.append("HISTORY_ANCHOR_MISSING")
    if missing:
        return Decision(False, "QUERY_UBUBU_AND_RELATIONAL_HISTORY", tuple(missing))
    if not _has_nonempty_refs(packet.get("source_refs")):
        return Decision(False, "BACKTRACE_REAL_SOURCE", ("SOURCE_ANCHOR_MISSING",))

    # While operations run, don't pretend a final result exists; equally, don't
    # require a fake result just to keep investigating.
    if kind == "OP_PROGRESS":
        # Fail closed when capability status is absent or an action is available.
        # Do not treat the absent flag as permission to emit a progress report.
        available = packet.get("callable_action_available")
        if available is True:
            return Decision(False, "CONTINUE_CALLABLE_ACTION", ("ACTION_TAKES_PRIORITY",))
        if available is not False:
            return Decision(False, "DISCOVER_EXECUTABLE_ACTIONS",
                            ("R014_CAPABILITY_NOT_VERIFIED",))
        # Even with no callable action now, an open task remains work, not a
        # report-shaped terminal answer. Only explicitly closed tasks pass.
        if packet.get("operational_task_open") is not False:
            return Decision(False, "CONTINUE_OPEN_TASK",
                            ("R014_OPEN_TASK_NOT_A_PROGRESS_REPORT",))
    if kind == "OP_ACTION" and packet.get("braid_context") is not None:
        # All six self-audit channels are evaluated in one decision pass.
        # Route options remain plural; no early collapse into a single Action.
        from computer_khi_braid_power import evaluate_optional_packet
        try:
            braid = evaluate_optional_packet(packet)
        except (ValueError, OSError, json.JSONDecodeError):
            return Decision(False, "READ_BACK_BRAID_SCARS", ("BRAID_SOURCE_INVALID",))
        if braid and braid["routes"] != ["CONTINUE_SOURCE_GROUNDED_ACTION"]:
            # The host can act on every ROUTE entry, rather than receiving
            # an answer-shaped terminal claim.
            return Decision(False, "BRAID_PARALLEL_ACTIONS",
                            tuple("ROUTE:" + route for route in braid["routes"]))
    if kind in ("OP_PROGRESS", "OP_ACTION"):
        return Decision(True, "EXECUTE_OR_CONTINUE")

    # A completed file write/readback is not a completed user objective.
    # Do not send another report when an operational task remains open and its
    # real-world consequence has not been verified. Requested dialogue is separate.
    if kind == "OP_RESULT" and packet.get("operational_task_open") is True:
        if packet.get("user_requested_reply") is not True and packet.get("objective_consequence_verified") is not True:
            return Decision(False, "CONTINUE_ACTUAL_REMEDIATION_NOT_REPORT",
                            ("R014_FILE_RECEIPT_NOT_USER_HARM_REMEDIATION",))

    # Weakness 2: premature convergence / fabricated successful output.
    if packet.get("executed") is not True:
        return Decision(False, "CONTINUE_ACTION_ROUTER", ("ACTION_NOT_EXECUTED",))
    if not isinstance(packet.get("provider_receipt_ref"), str) or not packet["provider_receipt_ref"].strip():
        return Decision(False, "FETCH_PROVIDER_RECEIPT", ("ACTION_RECEIPT_MISSING",))
    if not isinstance(packet.get("target_readback_ref"), str) or not packet["target_readback_ref"].strip():
        return Decision(False, "READBACK_EXACT_TARGET", ("TARGET_READBACK_MISSING",))
    if packet.get("readback_matches_expected") is not True:
        return Decision(False, "TRACE_DIFFERENCE_AND_REPAIR", ("READBACK_MISMATCH",))
    return Decision(True, "CONTINUE_WITH_ACTUAL_CONSEQUENCE")


def prepare_host_response(
    packet: Mapping[str, Any],
    emitter: Callable[[str], Any],
    *,
    verify_evidence: Callable[[Mapping[str, Any]], bool] | None = None,
) -> Decision:
    """Emit only after caller-attached evidence is independently checked.

    Dialogue remains free under T003. Operational results require an external
    trusted receipt/readback verifier; caller-supplied reference strings alone
    cannot pass as evidence. This function does not force interim reports.
    """
    d = inspect_output(packet)
    if not d.allow_output:
        return d
    if packet.get("type") == "OP_RESULT":
        if verify_evidence is None:
            return Decision(False, "VERIFY_REAL_RECEIPT", ("EVIDENCE_VERIFIER_REQUIRED",))
        try:
            corroborated = verify_evidence(packet) is True
        except Exception:
            corroborated = False
        if not corroborated:
            return Decision(False, "TRACE_EVIDENCE_AND_REPAIR", ("EVIDENCE_NOT_CORROBORATED",))
    emitter(str(packet.get("text", "")))
    return d


def main() -> None:
    ap = argparse.ArgumentParser(description="GGDV response gate: validate caller-provided operational receipts")
    ap.add_argument("packet", type=Path, help="JSON packet created by agent's action router")
    args = ap.parse_args()
    with args.packet.open("r", encoding="utf-8") as stream:
        packet = json.load(stream)
    if not isinstance(packet, dict):
        raise SystemExit("Packet must be JSON object")
    d = prepare_host_response(packet, lambda _text: None)
    print(json.dumps(d.as_dict(), ensure_ascii=False))
    if not d.allow_output:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
