#!/usr/bin/env python3
"""Offline preflight validator for TESSERACT FrankenMoE starter config."""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FAIL: PyYAML missing. Install requirements.txt first.")
    raise SystemExit(2)

PLACEHOLDER_PREFIX = "REPLACE_WITH_"


def main() -> int:
    root = Path(__file__).resolve().parent
    config_path = root / "mergekit-moe.yml"
    contract_path = root / "routing_contract.json"
    errors: list[str] = []

    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"FAIL: cannot parse config: {exc}")
        return 2

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    base = str(config.get("base_model", ""))
    if not base or base.startswith(PLACEHOLDER_PREFIX):
        errors.append("base_model is unresolved")
    experts = config.get("experts")
    if not isinstance(experts, list) or len(experts) < 2:
        errors.append("at least two experts are required")
    else:
        for index, expert in enumerate(experts):
            source = str(expert.get("source_model", ""))
            if not source or source.startswith(PLACEHOLDER_PREFIX):
                errors.append(f"experts[{index}].source_model is unresolved")
            for key in ("positive_prompts", "negative_prompts"):
                prompts = expert.get(key)
                if not isinstance(prompts, list) or not prompts or not all(
                    isinstance(item, str) and item.strip() for item in prompts
                ):
                    errors.append(f"experts[{index}].{key} must be a non-empty string list")
    if config.get("gate_mode") != "hidden":
        errors.append("gate_mode must be hidden for this starter design")
    if config.get("dtype") not in {"bfloat16", "float16", "float32"}:
        errors.append("dtype must be bfloat16, float16, or float32")
    if not contract.get("record_required_fields"):
        errors.append("routing contract has no required record fields")

    if errors:
        print("PREFLIGHT BLOCKED")
        for error in errors:
            print(f"- {error}")
        print("This is expected for the untouched template; resolve model IDs and rerun.")
        return 1
    print("PREFLIGHT PASS: structural checks only; model compatibility/build not yet tested.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
