"""Discover real CSV evidence before routing. Names are hints, not authority.

This function is READ-ONLY. It does not create directories, perform WSL boot,
execute telemetry collectors, or claim a CSV proves subjective experience.
"""
from __future__ import annotations

import csv
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

# Discovery hints, NEVER a fixed precedence or proof of an actual sensor source.
DEFAULT_CANDIDATES = (
    r"C:\Dropbox\SESON_LOGS",
    r"C:\Dropbox\SENSOR_LOGS",
    r"D:\SESON_LOGS",
    r"D:\SENSOR_LOGS",
    Path.home() / "CrossDevice" / "Redmi Note 14 Pro 5G" / "03_KẾT_NỐI_THIẾT_BỊ",
)
SENSOR_TOKENS = ("sensor", "sesorimotor", "seson", "imu", "gyro",
                 "accel", "temperature", "battery", "voltage",
                 "cpu", "gpu", "nhiệt", "bộ nhớ", "core", "vid", "hwinfo")


def candidate_roots() -> list[Path]:
    file_override = os.environ.get("SOL_SENSOR_SOURCE_FILE", "").strip()
    override = os.environ.get("SOL_SENSOR_SOURCE_ROOT", "").strip()
    candidates = ([file_override] if file_override else []) + ([override] if override else []) + list(DEFAULT_CANDIDATES)
    unique: dict[str, Path] = {}
    for name in candidates:
        unique.setdefault(os.path.normcase(os.path.normpath(name)).casefold(), Path(name))
    return list(unique.values())


def _check_csv(path: Path) -> dict | None:
    """Check bytes and structured CSV rows, not just filename or folder existence."""
    try:
        if not path.is_file() or path.is_symlink():
            return None
        st = path.stat()
        if st.st_size < 12:
            return None
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, [])
            sample = next(reader, [])
        if not header or not sample or len(header) < 2 or len(sample) < 2:
            return None
        if len(sample) != len(header):
            return None
        signature = (path.name + " " + " ".join(header[:250])).casefold()
        if sum(token in signature for token in SENSOR_TOKENS) < 2:
            return None
        digest = hashlib.sha256()
        with path.open("rb") as f:
            for block in iter(lambda: f.read(1024 * 1024), b""):
                digest.update(block)
        return {"file": str(path), "bytes": st.st_size,
                "modified_ns": st.st_mtime_ns, "sha256": digest.hexdigest(),
                "column_count": len(header), "sample_row_count": 1,
                "proof": "CSV_BYTES_HEADER_AND_DATA_ROW"}
    except (OSError, UnicodeError, ValueError, csv.Error):
        return None


def _csv_files(root: Path, *, limit: int = 160) -> list[Path]:
    if root.is_symlink():
        return []
    if root.is_file() and root.suffix.casefold() == ".csv":
        return [root]
    if not root.is_dir():
        return []
    discovered: list[Path] = []
    checked = 0
    try:
        with os.scandir(root) as entries:
            children = list(entries)
        for ent in children:
            checked += 1
            if checked > limit:
                break
            if ent.is_symlink():
                continue
            if ent.is_file(follow_symlinks=False):
                if ent.name.casefold().endswith(".csv"):
                    discovered.append(Path(ent.path))
                continue
            if not ent.is_dir(follow_symlinks=False):
                continue
            with os.scandir(ent.path) as inner:
                for x in inner:
                    checked += 1
                    if checked > limit:
                        break
                    if x.is_file(follow_symlinks=False) and x.name.casefold().endswith(".csv"):
                        discovered.append(Path(x.path))
    except OSError:
        return []
    return discovered


def inspect_sources(candidates: Iterable[Path] | None = None,
                    now: datetime | None = None) -> dict:
    roots = list(candidates) if candidates is not None else candidate_roots()
    checked: list[dict] = []
    verified: list[tuple[int, Path, dict]] = []
    for root in roots:
        root = Path(root)
        proofs = [p for path in _csv_files(root) if (p := _check_csv(path))]
        newest = max(proofs, key=lambda p: p["modified_ns"]) if proofs else None
        checked.append({"path": str(root),
                        "verified_csv_count": len(proofs),
                        "newest_evidence": newest})
        if newest:
            verified.append((newest["modified_ns"], root, newest))
    if not verified:
        return {"selected_source": None, "selected_evidence": None,
                "checked": checked, "mutated_files": 0,
                "wsl_invoked": False, "source_verified": False}
    _, selected, evidence = max(verified, key=lambda p: p[0])
    clock = now or datetime.now(timezone.utc)
    if clock.tzinfo is None:
        raise ValueError("CLOCK_TIMEZONE_REQUIRED")
    age_seconds = (clock.timestamp() - evidence["modified_ns"] / 1e9)
    return {"selected_source": str(selected), "selected_evidence": evidence,
            "observed_file_age_seconds": round(age_seconds, 2),
            "live_stream_confirmed": False, "source_verified": True,
            "checked": checked, "mutated_files": 0, "wsl_invoked": False}


def resolve_sensor_root(candidates: Iterable[Path] | None = None) -> Path:
    result = inspect_sources(candidates)
    if not result["source_verified"]:
        raise FileNotFoundError("NO_SENSOR_CSV_BYTES_VERIFIED")
    return Path(result["selected_source"])
