"""Locate an existing SENSOR/SESON carrier before choosing an execution route.

Non-mutating. An empty directory is not evidence of a live sensor source.
Never create a missing legacy D: directory to disguise a displaced source.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

DEFAULT_CANDIDATES = (
    r"C:\Dropbox\SESON_LOGS",  # original user spelling is a real locator
    r"C:\Dropbox\SENSOR_LOGS",
    r"D:\SESON_LOGS",
    r"D:\SENSOR_LOGS",
)


def candidate_roots() -> list[Path]:
    override = os.environ.get("SOL_SENSOR_SOURCE_ROOT", "").strip()
    names = ([override] if override else []) + list(DEFAULT_CANDIDATES)
    seen: set[str] = set()
    result: list[Path] = []
    for name in names:
        key = name.casefold()
        if key not in seen:
            seen.add(key)
            result.append(Path(name))
    return result


def count_real_files(root: Path, *, max_entries: int = 256) -> int:
    """Inspect metadata only, up to two levels, without following symlinks."""
    if not root.is_dir():
        return 0
    found = 0
    checked = 0
    try:
        with os.scandir(root) as entries:
            for entry in entries:
                checked += 1
                if checked > max_entries:
                    break
                if entry.is_file(follow_symlinks=False) and entry.stat(follow_symlinks=False).st_size > 0:
                    found += 1
                    continue
                if not entry.is_dir(follow_symlinks=False):
                    continue
                with os.scandir(entry.path) as nested:
                    for child in nested:
                        checked += 1
                        if checked > max_entries:
                            break
                        if child.is_file(follow_symlinks=False) and child.stat(follow_symlinks=False).st_size > 0:
                            found += 1
    except OSError:
        return 0
    return found


def inspect_sources(candidates: Iterable[Path] | None = None) -> dict:
    roots = list(candidates) if candidates is not None else candidate_roots()
    checks = []
    selected = None
    for root in roots:
        path = Path(root)
        files = count_real_files(path)
        checks.append({"path": str(path), "nonempty_files_found": files})
        if selected is None and files > 0:
            selected = path
    return {"selected_source": str(selected) if selected is not None else None,
            "checked": checks, "mutated_files": 0, "wsl_invoked": False}


def resolve_sensor_root(candidates: Iterable[Path] | None = None) -> Path:
    result = inspect_sources(candidates)
    if result["selected_source"] is None:
        raise FileNotFoundError("NO_OBSERVED_SENSOR_SOURCE: " +
                                ", ".join(x["path"] for x in result["checked"]))
    return Path(result["selected_source"])
