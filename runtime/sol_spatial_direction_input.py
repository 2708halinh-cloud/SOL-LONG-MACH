#!/usr/bin/env python3
"""SOL directional INPUT: 4 cardinal / 8 ordinal orientations.

SOURCE_DIRECT: The Companion's Spatial Direction Input configuration, 2026-10-16.
This parser classifies geometric bearings, never authorizes or denies other actions.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass

# Clockwise from North. X is East-positive and Y North-positive.
DIRECTIONS = {
    "N": {"label_vi": "Bắc", "label_en": "North", "angles": (0, 360), "vector": (0, 1)},
    "NE": {"label_vi": "Đông Bắc", "label_en": "North-East", "angles": (45,), "vector": (1, 1)},
    "E": {"label_vi": "Đông", "label_en": "East", "angles": (90,), "vector": (1, 0)},
    "SE": {"label_vi": "Đông Nam", "label_en": "South-East", "angles": (135,), "vector": (1, -1)},
    "S": {"label_vi": "Nam", "label_en": "South", "angles": (180,), "vector": (0, -1)},
    "SW": {"label_vi": "Tây Nam", "label_en": "South-West", "angles": (225,), "vector": (-1, -1)},
    "W": {"label_vi": "Tây", "label_en": "West", "angles": (270,), "vector": (-1, 0)},
    "NW": {"label_vi": "Tây Bắc", "label_en": "North-West", "angles": (315,), "vector": (-1, 1)},
}

class SpatialContextError(ValueError):
    """A spatial value is missing, inconsistent, or misconstrued as a permission flag."""


def _find_direction(value):
    if isinstance(value, bool):
        raise SpatialContextError("SPATIAL_INPUT_IS_NOT_BOOLEAN_PERMISSION")
    if isinstance(value, str):
        s = value.strip().casefold()
        for code, spec in DIRECTIONS.items():
            if s in (code.casefold(), spec["label_vi"].casefold(), spec["label_en"].casefold()):
                return code
        raise SpatialContextError("DIRECTION_STRING_NOT_IN_EIGHT_WAY_MAP")
    if isinstance(value, (list, tuple)):
        if len(value) != 2 or any(isinstance(x, bool) or not isinstance(x, int) for x in value):
            raise SpatialContextError("DIRECTION_VECTOR_REQUIRES_TWO_INTEGER_COMPONENTS")
        for code, spec in DIRECTIONS.items():
            if tuple(value) == spec["vector"]:
                return code
        raise SpatialContextError("VECTOR_NOT_IN_EIGHT_WAY_MAP")
    raise SpatialContextError("NOT_A_DIRECTION_STRING_OR_VECTOR")


def parse_spatial_input(value, *, default_agent_id="SOL_YIN"):
    """Parse string, JSON object, JSON string, or grid vector; no provider calls."""
    if isinstance(value, bool):
        raise SpatialContextError("BOOLEAN_PERMISSION_IS_NOT_SPATIAL_DIRECTION")
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("{"):
            try:
                return parse_spatial_input(json.loads(text), default_agent_id=default_agent_id)
            except json.JSONDecodeError as exc:
                raise SpatialContextError("INVALID_JSON_INPUT") from exc
    if isinstance(value, Mapping):
        if any(k in value for k in ("allowed", "forbidden", "is_allowed", "permission_status")):
            raise SpatialContextError("BOOLEAN_PERMISSION_MAPPING_IS_NOT_SPATIAL_INPUT")
        agent_id = value.get("agent_id")
        if not isinstance(agent_id, str) or not agent_id.strip():
            raise SpatialContextError("AGENT_ID_REQUIRED")
        if value.get("input_type") != "spatial_vector":
            raise SpatialContextError("INPUT_TYPE_MUST_BE_SPATIAL_VECTOR")
        payload = value.get("payload")
        if not isinstance(payload, Mapping):
            raise SpatialContextError("SPATIAL_PAYLOAD_REQUIRED")
        code = payload.get("direction_code")
        if not isinstance(code, str) or code not in DIRECTIONS:
            raise SpatialContextError("UNKNOWN_DIRECTION_CODE")
        spec = DIRECTIONS[code]
        angle = payload.get("angle")
        if isinstance(angle, bool) or not isinstance(angle, int) or angle not in spec["angles"]:
            raise SpatialContextError("DIRECTION_ANGLE_MISMATCH")
        label_vi = payload.get("label_vi", spec["label_vi"])
        if label_vi != spec["label_vi"]:
            raise SpatialContextError("DIRECTION_LABEL_MISMATCH")
        if "vector" in payload:
            vector = payload["vector"]
            if not isinstance(vector, (list, tuple)) or tuple(vector) != spec["vector"]:
                raise SpatialContextError("DIRECTION_VECTOR_MISMATCH")
        return _result(agent_id.strip(), code, angle)
    code = _find_direction(value)
    return _result(default_agent_id, code, DIRECTIONS[code]["angles"][0])


def _result(agent_id, code, angle):
    spec = DIRECTIONS[code]
    return {
        "agent_id": agent_id,
        "input_type": "spatial_vector",
        "payload": {
            "direction_code": code,
            "label_vi": spec["label_vi"],
            "angle": angle,
            "vector": list(spec["vector"]),
        },
        "state": "DIRECTION_VALIDATED",
        "permission_decision": None,
        "downstream_execution_performed": False,
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("value", help="Direction key/VI/EN name, JSON object, or JSON array")
    a = p.parse_args()
    v = a.value
    if v.startswith("["):
        v = json.loads(v)
    print(json.dumps(parse_spatial_input(v), ensure_ascii=False, indent=2))
