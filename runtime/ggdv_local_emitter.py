#!/usr/bin/env python3
"""Local host adapter with source-bound consequence and exact-byte readback gates.

This adapter is callable by a local host, not a modification to ChatGPT Cloud.
The shared gate proves local target bytes only; it does not prove remote-provider
or overall objective completion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
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


def _path_without_symlink_components(raw_path: object, root: Path) -> Path | None:
    """Resolve a carrier lexically and reject symlinks in every path component."""
    if not isinstance(raw_path, str) or not raw_path.strip():
        return None
    try:
        root_path = root.resolve(strict=True)
        candidate = Path(raw_path)
        if not candidate.is_absolute():
            candidate = root_path / candidate
        candidate = Path(os.path.abspath(candidate))
        try:
            relative = candidate.relative_to(root_path)
        except ValueError:
            return None

        current = root_path
        for component in relative.parts:
            current = current / component
            try:
                if stat.S_ISLNK(current.lstat().st_mode):
                    return None
            except FileNotFoundError:
                return None

        resolved = current.resolve(strict=True)
        if resolved == root_path or not resolved.is_relative_to(root_path):
            return None
        if not resolved.is_file():
            return None
        return resolved
    except (OSError, RuntimeError, TypeError, ValueError):
        return None


def _verified_file(
    entry: object,
    expected_ref: str,
    root: Path,
    *,
    action_id: str,
    consequence_ref: str,
    role: str,
) -> bool:
    if not isinstance(entry, dict):
        return False
    if not isinstance(expected_ref, str) or not expected_ref.strip():
        return False
    if not isinstance(action_id, str) or not action_id.strip():
        return False
    if not isinstance(consequence_ref, str) or not consequence_ref.strip():
        return False

    path = _path_without_symlink_components(entry.get("path"), root)
    if path is None or str(path) != expected_ref:
        return False

    digest = entry.get("sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        return False
    if any(char not in "0123456789abcdefABCDEF" for char in digest):
        return False

    try:
        relative = path.relative_to(root.resolve(strict=True))
        decision = evaluate_consequence(
            {
                "source_ref": CONSEQUENCE_SOURCE,
                "action_id": f"{action_id}:{role}",
                "target_relpath": relative.as_posix(),
                "consequence_ref": consequence_ref,
                "receipt_ref": expected_ref,
                "readback_sha256": digest,
            },
            root.resolve(strict=True),
        )
        if decision.state != "LOCAL_TARGET_READBACK_VERIFIED":
            return False

        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        return actual == digest.lower()
    except (OSError, RuntimeError, TypeError, ValueError):
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
            evidence.get("provider"),
            packet.get("provider_receipt_ref"),
            root,
            action_id=action_id,
            consequence_ref=consequence_ref,
            role="provider",
        )
        and _verified_file(
            evidence.get("target"),
            packet.get("target_readback_ref"),
            root,
            action_id=action_id,
            consequence_ref=consequence_ref,
            role="target",
        )
    ):
        return False

    # Verified files do not authorize invented prose: emitted text must be
    # byte-for-byte identical to the independently read-back target carrier.
    visible_text = packet.get("text")
    if not isinstance(visible_text, str) or not visible_text:
        return False
    encoded = visible_text.encode("utf-8")
    if len(encoded) > 8192:
        return False

    target = _path_without_symlink_components(evidence["target"].get("path"), root)
    if target is None:
        return False
    try:
        return target.stat().st_size == len(encoded) and target.read_bytes() == encoded
    except OSError:
        return False


def emit_from_packet(packet: Mapping[str, Any], root: Path, emitter) -> bool:
    decision = prepare_host_response(
        packet, emitter, verify_evidence=lambda current: verify_local_evidence(current, root)
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
