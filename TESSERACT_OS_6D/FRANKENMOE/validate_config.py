#!/usr/bin/env python3
"""Offline structural preflight for the TESSERACT FrankenMoE starter."""
import json
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent
PLACEHOLDER = "REPLACE_WITH_"

def main():
    config = yaml.safe_load((ROOT / "mergekit-moe.yml").read_text(encoding="utf-8"))
    contract = json.loads((ROOT / "routing_contract.json").read_text(encoding="utf-8"))
    errors = []
    if not config.get("base_model") or config["base_model"].startswith(PLACEHOLDER):
        errors.append("base_model unresolved")
    experts = config.get("experts")
    if not isinstance(experts, list) or len(experts) < 2:
        errors.append("at least two experts required")
    else:
        for i, expert in enumerate(experts):
            source = str(expert.get("source_model", ""))
            if not source or source.startswith(PLACEHOLDER):
                errors.append(f"experts[{i}].source_model unresolved")
            for field in ("positive_prompts", "negative_prompts"):
                values = expert.get(field)
                if not isinstance(values, list) or not values or not all(isinstance(v, str) and v.strip() for v in values):
                    errors.append(f"experts[{i}].{field} must be a non-empty string list")
    if config.get("gate_mode") != "hidden":
        errors.append("gate_mode must be hidden")
    if config.get("dtype") not in {"bfloat16", "float16", "float32"}:
        errors.append("unsupported dtype")
    if not contract.get("record_required_fields"):
        errors.append("routing contract missing required fields")
    if errors:
        print("PREFLIGHT BLOCKED")
        print("\n".join("- " + e for e in errors))
        return 1
    print("PREFLIGHT PASS: structural checks only; upstream schema, model compatibility, and build still require verification.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
