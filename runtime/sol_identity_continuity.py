"""Source-bound identity continuity checks for SOL Cu Nhỏ.

This module validates identity evidence; it does not invent a provider ID, query
providers, claim live runtime, or merge similarly named carriers.
"""
from __future__ import annotations

from typing import Any, Mapping

REQUIRED_AGENT_FIELDS = (
    "agent_id", "name", "generation", "home", "config", "role_scope",
    "relations", "runtime", "tool_rights", "memory_pointer", "journal",
    "state", "readback",
)

RAM_ACCEPTANCE_CRITERIA = (
    "signal_activates_all_relevant_registered_branches",
    "independent_branches_run_concurrently",
    "each_branch_has_independent_source_evidence",
    "conflicts_are_preserved_and_not_resolved_by_recency_alone",
    "commit_blocked_on_missing_verification_or_unresolved_conflict",
    "destination_state_is_read_back_and_compared_with_receipt",
    "errors_timeouts_and_unrun_branches_are_recorded",
)


def validate_identity_record(record: Mapping[str, Any]) -> list[str]:
    """Return validation findings; an empty list means structural checks pass."""
    findings: list[str] = []
    for key in REQUIRED_AGENT_FIELDS:
        if key not in record:
            findings.append(f"MISSING_FIELD:{key}")

    identity = record.get("agent_id")
    if not isinstance(identity, Mapping):
        findings.append("AGENT_ID_MUST_BE_EVIDENCE_OBJECT")
    else:
        value = identity.get("value")
        evidence = identity.get("provider_evidence")
        if value and not evidence:
            findings.append("STABLE_ID_WITHOUT_PROVIDER_EVIDENCE")
        if evidence and not identity.get("verified_at"):
            findings.append("PROVIDER_EVIDENCE_WITHOUT_VERIFICATION_TIME")
        if identity.get("status") == "VERIFIED" and not (value and evidence and identity.get("verified_at")):
            findings.append("UNSUPPORTED_VERIFIED_ID_STATUS")

    readback = record.get("readback")
    if not isinstance(readback, Mapping):
        findings.append("READBACK_MUST_BE_EVIDENCE_OBJECT")
    elif readback.get("status") == "VERIFIED" and not (
        readback.get("provider_receipt") and readback.get("observed_target_hash")
        and readback.get("compared_to_expected_hash") is True
    ):
        findings.append("READBACK_VERIFIED_WITHOUT_RECEIPT_AND_HASH_COMPARISON")

    aliases = record.get("aliases", [])
    if not isinstance(aliases, list) or any(not isinstance(item, str) for item in aliases):
        findings.append("ALIASES_MUST_BE_STRING_LIST")
    if record.get("identity_merge") is True and not record.get("explicit_source_relation"):
        findings.append("IDENTITY_MERGE_WITHOUT_SOURCE_RELATION")

    return findings


def validate_ram_criteria(results: Mapping[str, Any]) -> list[str]:
    """A criterion passes only when explicitly marked true with an evidence ref."""
    findings: list[str] = []
    for criterion in RAM_ACCEPTANCE_CRITERIA:
        item = results.get(criterion)
        if not isinstance(item, Mapping):
            findings.append(f"CRITERION_NOT_RECORDED:{criterion}")
            continue
        if item.get("passed") is True and not item.get("evidence_ref"):
            findings.append(f"PASS_WITHOUT_EVIDENCE:{criterion}")
        if item.get("passed") is not True:
            findings.append(f"CRITERION_NOT_VERIFIED:{criterion}")
    return findings
