#!/usr/bin/env python3
"""Source-bound continuity ledger for SOL agents.

This module records identity and lifecycle evidence without inventing missing IDs.
It is an offline local-file tool; it does not connect to Drive, GitHub, ChatGPT Memory,
or a device unless a separate authorized adapter supplies observations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "SOL_AGENT_CONTINUITY_V1"
EVENT_SCHEMA = "SOL_AGENT_EVENT_V1"
IDENTITY_FIELDS = (
    "agent_id", "name", "gen_seed", "home", "config", "role_scope",
    "relation", "runtime", "tool_rights", "memory_pointer", "journal",
    "state", "readback",
)


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_source_refs(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_nonempty_string(ref) for ref in value)


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    """Return validation errors. Unknown identity remains OPEN; it is never guessed."""
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        return ["MANIFEST_SCHEMA_MISMATCH"]

    errors: list[str] = []
    identity = manifest.get("identity")
    if not isinstance(identity, dict):
        return ["IDENTITY_OBJECT_REQUIRED"]

    for field in IDENTITY_FIELDS:
        if field not in identity:
            errors.append(f"IDENTITY_FIELD_MISSING:{field}")
        elif not isinstance(identity[field], (str, dict, list, type(None))):
            errors.append(f"IDENTITY_FIELD_TYPE_INVALID:{field}")

    if not _nonempty_string(identity.get("name")):
        errors.append("AGENT_NAME_REQUIRED")

    agent_id = identity.get("agent_id")
    if agent_id is None or (isinstance(agent_id, str) and not agent_id.strip()):
        errors.append("STABLE_AGENT_ID_UNRESOLVED")
    elif not isinstance(agent_id, str):
        errors.append("STABLE_AGENT_ID_TYPE_INVALID")

    if not _valid_source_refs(manifest.get("source_refs")):
        errors.append("SOURCE_PROVENANCE_REQUIRED")

    identity_status = manifest.get("identity_status")
    if not isinstance(identity_status, str) or not identity_status.strip():
        errors.append("IDENTITY_STATUS_REQUIRED")

    # Treat case/whitespace variants of VERIFIED as attempted verification,
    # then reject non-canonical spelling rather than bypassing the gate.
    if isinstance(identity_status, str) and identity_status.strip().upper() == "VERIFIED":
        if identity_status != "VERIFIED":
            errors.append("IDENTITY_STATUS_NONCANONICAL")
        if not _nonempty_string(agent_id) or manifest.get("independent_readback") is not True:
            errors.append("VERIFIED_STATUS_REQUIRES_ID_AND_BOOLEAN_READBACK")

    return errors


def make_event(event: dict[str, Any], *, previous_hash: str | None = None) -> dict[str, Any]:
    """Create a hash-chained event. The hash detects changes; it does not prove truth."""
    if not isinstance(event, dict):
        raise ValueError("EVENT_OBJECT_REQUIRED")

    event_id = event.get("event_id")
    kind = event.get("kind")
    source_refs = event.get("source_refs", [])
    if not _nonempty_string(event_id) or not _nonempty_string(kind) or not _valid_source_refs(source_refs):
        raise ValueError("EVENT_ID_KIND_AND_SOURCE_REFS_REQUIRED")

    body = {
        "schema": EVENT_SCHEMA,
        "event_id": event_id,
        "occurred_at": event.get("occurred_at") or datetime.now(timezone.utc).isoformat(),
        "kind": kind,
        "source_refs": source_refs,
        "observation": event.get("observation"),
        "action": event.get("action"),
        "outcome": event.get("outcome"),
        "previous_hash": previous_hash,
    }
    body["event_hash"] = sha256(canonical_json(body))
    return body


def verify_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Check event order and hash-chain integrity; never label source facts verified."""
    previous_hash = None
    errors: list[str] = []
    seen: set[str] = set()

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            errors.append(f"EVENT_OBJECT_REQUIRED:{index}")
            continue
        if event.get("schema") != EVENT_SCHEMA:
            errors.append(f"EVENT_SCHEMA_MISMATCH:{index}")
            continue

        event_id = event.get("event_id")
        if not _nonempty_string(event_id):
            errors.append(f"EVENT_ID_INVALID:{index}")
        elif event_id in seen:
            errors.append(f"DUPLICATE_EVENT_ID:{index}")
        else:
            seen.add(event_id)

        if not _nonempty_string(event.get("kind")) or not _valid_source_refs(event.get("source_refs")):
            errors.append(f"EVENT_FIELDS_INVALID:{index}")

        if event.get("previous_hash") != previous_hash:
            errors.append(f"PREVIOUS_HASH_MISMATCH:{index}")

        claimed = event.get("event_hash")
        body = {key: value for key, value in event.items() if key != "event_hash"}
        if not isinstance(claimed, str) or claimed != sha256(canonical_json(body)):
            errors.append(f"EVENT_HASH_MISMATCH:{index}")
        previous_hash = claimed

    return {
        "schema": "SOL_AGENT_EVENT_CHAIN_CHECK_V1",
        "event_count": len(events),
        "chain_integrity": "PASS" if not errors else "FAIL",
        "errors": errors,
        "source_truth_verified": False,
        "meaning": "Hash-chain integrity only; independently verify each source and read back each destination.",
    }


def append_event(path: Path, event: dict[str, Any]) -> dict[str, Any]:
    """Append one event without replacing prior bytes; reject a broken existing chain."""
    path.parent.mkdir(parents=True, exist_ok=True)
    events: list[dict[str, Any]] = []
    if path.exists():
        raw = path.read_text(encoding="utf-8")
        events = [json.loads(line) for line in raw.splitlines() if line.strip()]
        check = verify_events(events)
        if check["chain_integrity"] != "PASS":
            raise ValueError("EXISTING_EVENT_CHAIN_INVALID; refusing append")

    previous_hash = events[-1]["event_hash"] if events else None
    record = make_event(event, previous_hash=previous_hash)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        stream.flush()
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate-manifest")
    validate.add_argument("manifest", type=Path)
    verify = sub.add_parser("verify-events")
    verify.add_argument("journal", type=Path)
    args = parser.parse_args()

    if args.command == "validate-manifest":
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        errors = validate_manifest(manifest)
        print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
        return 0 if not errors else 2
    events = [json.loads(line) for line in args.journal.read_text(encoding="utf-8").splitlines() if line.strip()]
    result = verify_events(events)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["chain_integrity"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
