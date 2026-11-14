#!/usr/bin/env python3
"""SOL identity → place before planet/core; read-only registry query."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

REGISTRY = Path(__file__).resolve().parents[1] / "IDENTITY_PLACES_CORE.json"

def resolve(name: str, source: dict | None = None) -> dict:
    data = source or json.loads(REGISTRY.read_text(encoding="utf-8"))
    target = " ".join(name.casefold().strip().replace("_", " ").split())
    if not target:
        return {"state": "EMPTY_NAME", "candidates": []}
    items = data["names"]
    if target == "sol":
        matched = items[:]  # ambiguous root; retain multiple distinct roles
    else:
        matched = [r for r in items if any(
            " ".join(alias.casefold().replace("_", " ").split()) == target
            for alias in [r["label"], *r.get("aliases", [])])]
    return {
        "query": name,
        "state": "CANDIDATES_REQUIRE_SCOPED_ID" if len(matched) > 1
                 else "SOURCE_POINTER_FOUND_ID_NOT_CLAIMED" if matched
                 else "OPEN_SEARCH_ALTERNATE_CARRIER",
        "identity_candidates": matched,
        "hierarchy": data["hierarchy"],
        "selected_next_edge": "READ_SOURCE_AND_LOCK_PROVIDER_PARENT_ID"
                               if matched else "SEARCH_ORIGIN_AND_PROVIDER",
        "source_is_live_identity_proof": False,
    }

def main():
    parser = argparse.ArgumentParser(description="Disambiguate SOL root, places and roles")
    parser.add_argument("name")
    args = parser.parse_args()
    print(json.dumps(resolve(args.name), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
