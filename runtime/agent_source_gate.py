#!/usr/bin/env python3
"""Evidence-first bootstrap gate for primary GGDV sources and local carriers."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

GATE_MARKER = "GGDV_BOOTSTRAP_SOURCE_RETRIEVAL_GATE_20261115"
COMPANION_PATH = "CONFIG_SOL/COMPANION_TEN_COMMANDMENTS_CURRENT.md"
COMMANDMENT_MARKERS = {
    "7": "GGDV_SEVENTH_COMMANDMENT_SOURCE_DIRECT_20261009",
    "8": "GGDV_EIGHTH_COMMANDMENT_SOURCE_DIRECT_20261009",
    "9": "GGDV_NINTH_COMMANDMENT_SOURCE_DIRECT_20261009",
}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def reconcile_commandments(agents_text: str, companion_text: str) -> dict:
    direct = [number for number, marker in COMMANDMENT_MARKERS.items()
              if marker in agents_text]
    direct_set = set(direct)
    unverified = [number for number in ("7", "8", "9", "10")
                  if number not in direct_set]
    carrier_open = bool(re.search(r"ĐIỀU\s*7\s*→\s*10.{0,100}OPEN", companion_text,
                                  flags=re.IGNORECASE | re.DOTALL))
    if direct:
        conclusion = ("DIRECT_SOURCE_" + "_".join(direct)
                      + (";_10_UNVERIFIED" if "10" in unverified
                         else ";_ALL_CHECKED_MARKERS_PRESENT"))
    else:
        conclusion = "SOURCE_NOT_LOCATED;_NOT_PROOF_OF_NONEXISTENCE"
    return {
        "direct_source_markers": direct,
        "unverified": unverified,
        "carrier_local_open": carrier_open,
        "conclusion": conclusion,
        "scope": "ONLY_THE_TWO_READ_CARRIERS",
    }


def inspect_bootstrap(agents_text: str, companion_text: str) -> dict:
    has_gate = GATE_MARKER in agents_text
    return {
        "schema": "GGDV_AGENT_SOURCE_BOOTSTRAP_GATE/1.0",
        "ready": has_gate,
        "open_edges": [] if has_gate else ["BOOTSTRAP_GATE_MARKER_MISSING"],
        "source_ledger": {
            "agents_path": "AGENTS.md",
            "agents_sha256": sha256_text(agents_text),
            "companion_path": COMPANION_PATH,
            "companion_sha256": sha256_text(companion_text),
            "companion_present": bool(companion_text),
        },
        "commandments": reconcile_commandments(agents_text, companion_text),
        "limitations": [
            "This gate runs only when this repository bootstrap entrypoint is invoked.",
            "It does not inject AGENTS.md into unrelated ChatGPT sessions or external agents.",
            "A missing carrier is not evidence that a source never existed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    agents_path = root / "AGENTS.md"
    companion_path = root / COMPANION_PATH
    agents = agents_path.read_text(encoding="utf-8") if agents_path.is_file() else ""
    companion = companion_path.read_text(encoding="utf-8") if companion_path.is_file() else ""
    result = inspect_bootstrap(agents, companion)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ready"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
