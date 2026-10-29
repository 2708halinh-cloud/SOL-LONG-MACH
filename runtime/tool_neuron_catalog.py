#!/usr/bin/env python3
"""Convert observed platform/library tool inventories into portable neuron descriptors.

This is a metadata transform only. It never calls a tool, authenticates a provider,
or treats a catalog entry as permission to execute.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

INPUT_SCHEMA = "TESSERACT_TOOL_INVENTORY_V1"
OUTPUT_SCHEMA = "TESSERACT_TOOL_NEURON_CATALOG_V1"

def _required_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}_REQUIRED")
    return value.strip()

def build_catalog(inventories: list[dict[str, Any]]) -> dict[str, Any]:
    neurons = []
    seen = set()
    receipts = []
    for inventory in inventories:
        if inventory.get("schema") != INPUT_SCHEMA:
            raise ValueError("INVENTORY_SCHEMA_MISMATCH")
        source_id = _required_text(inventory.get("source_id"), "SOURCE_ID")
        observed_at = _required_text(inventory.get("observed_at"), "OBSERVED_AT")
        tools = inventory.get("tools")
        if not isinstance(tools, list):
            raise ValueError("TOOLS_ARRAY_REQUIRED")
        receipts.append({"source_id": source_id, "observed_at": observed_at, "count": len(tools)})
        for item in tools:
            if not isinstance(item, dict):
                raise ValueError("TOOL_DESCRIPTOR_MUST_BE_OBJECT")
            name = _required_text(item.get("name"), "TOOL_NAME")
            description = _required_text(item.get("description"), "TOOL_DESCRIPTION")
            source_ref = _required_text(item.get("source_ref"), "SOURCE_REF")
            effect_raw = item.get("effect")
            effect = "readOnly" if effect_raw == "readOnly" else "externalMutation"
            identity = "\0".join((source_id, source_ref, name))
            suffix = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:10]
            slug = re.sub(r"[^A-Z0-9]+", "_", name.upper()).strip("_")[:48] or "TOOL"
            neuron_id = f"TOOL_{slug}_{suffix}"
            if neuron_id in seen:
                raise ValueError(f"DUPLICATE_NEURON_ID:{neuron_id}")
            seen.add(neuron_id)
            next_ids = item.get("suggested_next_neuron_ids", [])
            if not isinstance(next_ids, list) or any(not isinstance(x, str) or not x.strip() for x in next_ids):
                raise ValueError(f"INVALID_NEXT_NEURONS:{name}")
            neurons.append({
                "id": neuron_id,
                "name": name,
                "description": description,
                "source": f"{source_id}:{source_ref}",
                "effect": effect,
                "suggestedNextNeuronIDs": next_ids,
                "routing": {"input": "DENDRITES_EMBEDDING", "execution": "SOMA_ADAPTER", "output": "AXON_READBACK"},
                "authorization": "NOT_INFERRED",
                "status": "DESCRIPTOR_ONLY_NOT_EXECUTED"
            })
    known = {n["id"] for n in neurons}
    for neuron in neurons:
        dangling = [x for x in neuron["suggestedNextNeuronIDs"] if x not in known]
        if dangling:
            raise ValueError(f"UNKNOWN_NEXT_NEURON:{neuron['id']}:{','.join(dangling)}")
    return {
        "schema": OUTPUT_SCHEMA,
        "policy": {
            "one_neuron_per_observed_tool": True,
            "unknown_effect_defaults_to": "externalMutation",
            "provider_authorization_inferred": False,
            "tool_execution_performed": False,
            "fresh_inventory_required": True
        },
        "source_receipts": receipts,
        "neuron_count": len(neurons),
        "neurons": neurons
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inventories", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    inventories = [json.loads(p.read_text(encoding="utf-8")) for p in args.inventories]
    catalog = build_catalog(inventories)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {catalog['neuron_count']} neuron descriptors to {args.output}; no tools executed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
