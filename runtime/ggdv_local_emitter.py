#!/usr/bin/env python3
"""Local host adapter: only emit source-authored text after real file readback.

This adapter is callable by a local host, not a modification to ChatGPT Cloud.
No report is generated. OP_RESULT uses exact SHA-256 of provider and target
carriers under an explicitly authorized root. An arbitrary ref string is insufficient.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from ggdv_response_gate import prepare_host_response


def _verified_file(entry: object, expected_ref: str, root: Path) -> bool:
    if not isinstance(entry, dict) or not expected_ref:
        return False
    try:
        path = Path(str(entry["path"])).resolve(strict=True)
        if not path.is_file() or not path.is_relative_to(root.resolve(strict=True)):
            return False
        if str(path) != expected_ref:
            return False
        digest = str(entry["sha256"]).lower()
        if len(digest) != 64 or not all(c in "0123456789abcdef" for c in digest):
            return False
        sha = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                sha.update(chunk)
        return sha.hexdigest() == digest
    except (OSError, KeyError, TypeError, ValueError):
        return False


def verify_local_evidence(packet: Mapping[str, Any], root: Path) -> bool:
    evidence = packet.get("evidence_files")
    if not isinstance(evidence, dict):
        return False
    if not (
        _verified_file(evidence.get("provider"), str(packet.get("provider_receipt_ref", "")), root)
        and _verified_file(evidence.get("target"), str(packet.get("target_readback_ref", "")), root)
    ):
        return False
    # Literal source-only emission: verified files do not authorize invented prose.
    # The host must separately choose a safe, non-secret text carrier to publish.
    visible_text = packet.get("text")
    if not isinstance(visible_text, str) or not visible_text:
        return False
    encoded = visible_text.encode("utf-8")
    if len(encoded) > 8192:
        return False
    try:
        target = Path(str(evidence["target"]["path"])).resolve(strict=True)
        if target.stat().st_size != len(encoded):
            return False
        return target.read_bytes() == encoded
    except (OSError, KeyError, TypeError, ValueError):
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
