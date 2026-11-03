#!/usr/bin/env python3
"""Fail with exact Git-tracked paths that cannot round-trip through Windows."""
from __future__ import annotations
import collections
import subprocess
import sys

INVALID_CHARS = set('<>:"|?*')
RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}

def main() -> int:
    raw = subprocess.check_output(["git", "ls-tree", "-rz", "--name-only", "HEAD"])
    paths = [p.decode("utf-8", "surrogateescape") for p in raw.split(b"\0") if p]
    invalid = []
    children = collections.defaultdict(list)
    for path in paths:
        parts = path.split("/")
        reasons = []
        for part in parts:
            stem = part.split(".", 1)[0].upper()
            if any(ch in INVALID_CHARS for ch in part):
                reasons.append("windows-illegal-character")
            if part.endswith((" ", ".")):
                reasons.append("trailing-space-or-dot")
            if stem in RESERVED:
                reasons.append("reserved-device-name")
        if reasons:
            invalid.append((path, sorted(set(reasons))))
        for i, part in enumerate(parts):
            parent = "/".join(parts[:i]).casefold()
            children[parent].append((part, "/".join(parts[:i + 1])))
    collisions = []
    for parent, rows in children.items():
        folded = collections.defaultdict(set)
        for name, full in rows:
            folded[name.casefold()].add(full)
        for group in folded.values():
            if len(group) > 1:
                collisions.append((parent, sorted(group)))
    print(f"tracked_paths={len(paths)} invalid_windows_paths={len(invalid)} case_collisions={len(collisions)}")
    for path, reasons in invalid:
        print("INVALID", ",".join(reasons), path)
    for parent, group in collisions:
        print("CASE_COLLISION", parent, " | ".join(group))
    return 1 if invalid or collisions else 0

if __name__ == "__main__":
    raise SystemExit(main())
