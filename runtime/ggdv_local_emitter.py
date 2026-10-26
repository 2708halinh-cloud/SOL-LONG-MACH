#!/usr/bin/env python3
"""Local host adapter: only emit source-authored text after real file readback.

This adapter is callable by a local host, not a modification to ChatGPT Cloud.
OP_RESULT requires exact SHA-256 verification of provider and target carriers
under an explicitly authorized root, plus the shared consequence gate. The gate
only proves local target bytes; it does not prove remote-provider or objective
completion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

try:
    from ggdv_response_gate import prepare_host_response
except ImportError:  # package import from repository root
    from runtime.ggdv_response_gate import prepare_host_response

try:
    from companion_consequence_gate import SOURCE as CONSEQUENCE_SOURCE, evaluate as evaluate_consequence
except ImportError:  # package import from repository root
    from runtime.companion_consequence_gate import SOURCE as CONSEQUENCE_SOURCE, evaluate as evaluate_consequence


def _gate_file(
    entry: object,
    expected_ref: str,
    root: Path,
    *,
    action_id: str,
    consequence_ref: str,
    role: str,
) -> bool:
    """Apply the shared source-bound gate before the adapter opens evidence bytes."""
    if not isinstance(entry, dict) or not isinstance(expected_ref, str) or not expected_ref.strip():
        return False
    if not isinstance(action_id, str) or not action_id.strip():
        return False
    if not isinstance(consequence_ref, str) or not consequence_ref.strip():
        return False
    try:
        root_path = root.resolve(strict=True)
        raw_path = entry.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            return False
        candidate = Path(raw_path)
        if not candidate.is_absolute():
            candidate = root_path / candidate
        try:
            relative = candidate.relative_to(root_path)
        except ValueError:
            return False

        decision = evaluate_consequence(
            {
                "source_ref": CONSEQUENCE_SOURCE,
                "action_id": f"{action_id}:{role}",
                "target_relpath": relative.as_posix(),
                "consequence_ref": consequence_ref,
                "receipt_ref": expected_ref,
                "readback_sha256": entry.get("sha256"),
            },
            root_path,
        )
        return decision.state == "LOCAL_TARGET_READBACK_VERIFIED"
    except (OSError, RuntimeError, TypeError, ValueError):
        return False


def _verified_file(
    entry: object,
    expected_ref: str,
    root: Path,
    *,
    action_id: str,
    consequence_ref: str,
    role: str,
) -> bool:
    if not _gate_file(
        entry, expected_ref, root,
        action_id=action_id, consequence_ref=consequence_ref, role=role,
    ):
        return False
    try:
        path_value = entry.get("path")
        path = Path(path_value)
        if not path.is_absolute():
            path = root.resolve(strict=True) / path
        path = path.resolve(strict=True)
        root_path = root.resolve(strict=True)
        if not path.is_file() or not path.is_relative_to(root_path):
            return False
        if str(path) != expected_ref:
            return False
        digest = entry.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            return False
        if not all(c in "0123456789abcdefABCDEF" for c in digest):
            return False
        sha = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                sha.update(chunk)
        return sha.hexdigest() == digest.lower()
    except (OSError, KeyError, TypeError, ValueError, RuntimeError):
        return False


def verify_local_evidence(packet: Mapping[str, Any], root: Path) -> bool:
    evidence = packet.get("evidence_files")
    source_refs = packet.get("source_refs")
    action_id = packet.get("action_id")
    consequence_ref = packet.get("consequence_ref")
    if not isinstance(evidence, dict):
        return False
    if not isinstance(source_refs, list) or CONSEQUENCE_SOURCE not in source_refs:
        return False
    if not isinstance(action_id, str) or not action_id.strip():
        return False
    if not isinstance(consequence_ref, str) or not consequence_ref.strip():
        return False
    if not (
        _verified_file(
            evidence.get("provider"), str(packet.get("provider_receipt_ref", "")), root,
            action_id=action_id, consequence_ref=consequence_ref, role="provider",
        )
        and _verified_file(
            evidence.get("target"), str(packet.get("target_readback_ref", "")), root,
            action_id=action_id, consequence_ref=consequence_ref, role="target",
        )
    ):
        return False

    # Literal source-only emission: verified files do not authorize invented prose.
    visible_text = packet.get("text")
    if not isinstance(visible_text, str) or not visible_text:
        return False
    encoded = visible_text.encode("utf-8")
    if len(encoded) > 8192:
        return False
    try:
        target_entry = evidence["target"]
        target_value = target_entry["path"]
        target = Path(target_value)
        if not target.is_absolute():
            target = root.resolve(strict=True) / target
        target = target.resolve(strict=True)
        if target.stat().st_size != len(encoded):
            return False
        return target.read_bytes() == encoded
    except (OSError, KeyError, TypeError, ValueError, RuntimeError):
        return False


def emit_from_packet(packet: Mapping[str, Any], root: Path, emitter) -> bool:
    decision = prepare_host_response(
        packet, emitter, verify_evidence=lambda p: verify_local_evidence(p, root)
    )
    return decision.allow_output


def main() -> None:
    parser = argparse.ArgumentParser(description="Local verified T003/BIHM emission")
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--receipts-root", type=Path, required=True)
    args = parser.parse_args()
    packet = json.loads(args.packet.read_text(encoding="utf-8-sig"))
    if not isinstance(packet, dict):
        raise SystemExit(2)
    if not emit_from_packet(packet, args.receipts_root, print):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
