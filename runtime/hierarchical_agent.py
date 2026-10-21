#!/usr/bin/env python3
"""User-supplied hierarchical file-graph SIMULATION and six-source projection gate.

This module does not browse any real filesystem or call a language model.
For actual Windows physical traversal, retain the existing
G:\OS_Workspace\TESSERACT_OS\runtime\hierarchical_graph_router.py.
"""
from __future__ import annotations

import json
import sys
from typing import Any, Mapping


DEMO_SPACE = {
    "C:": {
        "Users": {
            "Halin": {
                ".config": ["config.json", "settings.ini"],
                "Documents": ["resume.pdf"],
            },
            "Guest": {},
        },
        "Windows": {"System32": {}},
    }
}

SIX_KEYS = (
    "DA_MIND 🟡",
    "MAU_REALITY 🔴",
    "THIT_SOUL 🟠",
    "XUONG_SPACE 🔵",
    "TOC_TIME 🟢",
    "KHI_POWER 🟣",
)


class HierarchicalNavigator:
    """Iterative direct-child traversal over an explicit, simulated graph."""

    def __init__(self, space_matrix: Mapping[str, Any], root: str = "C:"):
        if root not in space_matrix:
            raise ValueError("ROOT_MISSING_FROM_SUPPLIED_GRAPH")
        self.matrix = space_matrix
        self.root = root
        self.current_node = root
        self.path_history = [root]

    def _parts(self, path: str) -> list[str]:
        if not isinstance(path, str) or "\x00" in path:
            raise ValueError("INVALID_PATH")
        parts = [p for p in path.replace("\\", "/").split("/") if p]
        if not parts or parts[0] != self.root or any(p in (".", "..") for p in parts):
            raise ValueError("PATH_NOT_WITHIN_SIMULATED_ROOT")
        return parts

    def list_dir(self, current_path: str) -> dict[str, Any]:
        parts = self._parts(current_path)
        cursor: Any = self.matrix[parts[0]]
        for part in parts[1:]:
            if not isinstance(cursor, dict) or part not in cursor:
                return {"error": "NOT_A_VERIFIED_DIRECT_CHILD", "path": current_path}
            cursor = cursor[part]
        if isinstance(cursor, dict):
            children = list(cursor.keys())
        elif isinstance(cursor, list):
            children = list(cursor)
        else:
            children = []
        return {
            "parent": parts[-2] if len(parts) > 1 else None,
            "current": parts[-1],
            "children": children,
            "kind": "directory" if isinstance(cursor, dict) else "listed_leaf",
            "source": "DEMO_SPACE_ONLY",
        }

    def execute_traversal(self, target_path: str) -> dict[str, Any]:
        parts = self._parts(target_path)
        current_path = self.root
        self.current_node = self.root
        self.path_history = [self.root]
        steps = []
        for next_child in parts[1:]:
            scan = self.list_dir(current_path)
            if "error" in scan or scan["kind"] != "directory" or next_child not in scan["children"]:
                return {
                    "ok": False, "reason": "NOT_A_VERIFIED_DIRECT_CHILD",
                    "blocked_at": current_path, "requested_child": next_child,
                    "steps": steps, "readback_verified": False,
                }
            parent_path = current_path
            current_path = current_path + "\\" + next_child
            self.path_history.append(next_child)
            self.current_node = current_path
            steps.append({"parent": parent_path, "child": next_child, "edge": "DIRECT_CHILD",
                          "source": "DEMO_SPACE_ONLY"})
        return {
            "ok": True, "reached": current_path, "steps": steps,
            "path_history": list(self.path_history),
            "readback_verified": True, "proof_scope": "SIMULATED_GRAPH_ONLY",
        }


def project_six_from_supplied_source(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Copy only explicitly supplied, source-linked views. Never infer personal facts."""
    source = packet.get("origin_source")
    source_id = packet.get("entity_id")
    views = packet.get("projections")
    if not isinstance(source, str) or not source or not isinstance(source_id, str) or not source_id:
        raise ValueError("EXPLICIT_SOURCE_REF_AND_ENTITY_ID_REQUIRED")
    if not isinstance(views, dict) or any(key not in views for key in SIX_KEYS):
        raise ValueError("ALL_SIX_EXPLICIT_PROJECTIONS_REQUIRED")
    if any(not isinstance(views[key], dict) for key in SIX_KEYS):
        raise ValueError("PROJECTIONS_MUST_BE_OBJECTS")
    return {
        "entity_id": source_id,
        "origin_source": source,
        "projections": {key: views[key].copy() for key in SIX_KEYS},
        "projection_count": 6,
        "inference_applied": False,
        "readback_verified": False,
        "verification_scope": "STRUCTURE_ONLY_NOT_SOURCE_FILE_BYTES",
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\Halin\.config"
    result = HierarchicalNavigator(DEMO_SPACE).execute_traversal(target)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 2)
