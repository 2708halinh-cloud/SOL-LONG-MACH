#!/usr/bin/env python3
"""READ-ONLY HWiNFO and sensor-carrier discovery. No filesystem mutations.

Directory names are search hints, not evidence. The only proof is observed
CSV structure and, for 'live', file growth/change between two measurements.
Do not inspect or expose secrets in .codex.
"""
from __future__ import annotations
import argparse
import csv
import io
import json
import os
import re
import subprocess
import time
from collections import deque
from pathlib import Path

NAME = re.compile(r"hwinfo|hw[-_ ]?info|sensor|seson|sesori|telemetry|modual|affect|imu|log", re.I)
FIELDS = re.compile(r"battery|voltage|temp|gyro|acceler|cpu|gpu|fan|sensors|power|clock|rpm|mhz|°c|\[v\]|\[w\]", re.I)
EXT = {".csv", ".jsonl", ".log", ".tsv", ".txt"}

def roots():
    home = Path.home()
    return [home / "CrossDevice" / "Redmi Note 14 Pro 5G" / "03_KẾT_NỐI_THIẾT_BỊ",
            Path(r"C:\Dropbox"), Path(r"D:\SESON_LOGS"), Path(r"D:\SENSOR_LOGS"),
            home / "Documents", home / "Dropbox", home / ".codex",
            Path(r"D:\PHÒNG CHỈ HUY\.codex"), Path(r"C:\Users\halin\.codex")]

def candidates(places, max_entries=90000, max_seconds=75, depth_limit=7):
    pending = deque((Path(p), 0) for p in places)
    visited, found, count = set(), [], 0
    started = time.monotonic()
    while pending and count < max_entries and time.monotonic() - started < max_seconds:
        folder, depth = pending.popleft()
        key = os.path.normcase(str(folder)).casefold()
        if key in visited:
            continue
        visited.add(key)
        if not folder.is_dir() or folder.is_symlink() or depth > depth_limit:
            continue
        try:
            with os.scandir(folder) as items:
                for entry in items:
                    count += 1
                    if count >= max_entries:
                        break
                    try:
                        if entry.is_symlink():
                            continue
                        if entry.is_dir(follow_symlinks=False) and depth < depth_limit:
                            pending.append((Path(entry.path), depth + 1))
                        elif entry.is_file(follow_symlinks=False):
                            p = Path(entry.path)
                            if p.suffix.casefold() in EXT and NAME.search(str(p)):
                                found.append(p)
                    except OSError:
                        continue
        except OSError:
            continue
    return found, {"enumerated_entries": count,
                   "truncated": bool(pending or count >= max_entries)}

def inspect(path):
    try:
        st = path.stat()
        result = {"path": str(path), "bytes": st.st_size, "modified_ns": st.st_mtime_ns}
        if path.suffix.casefold() not in (".csv", ".tsv") or st.st_size < 12:
            return result
        with path.open("rb") as handle:
            raw = handle.read(120000)
        encoding = "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
        value = raw.decode(encoding, errors="replace")
        lines = value.splitlines()
        if len(lines) < 2:
            return result
        separator = ";" if lines[0].count(";") > lines[0].count(",") else ","
        rows = csv.reader(io.StringIO(value), delimiter=separator)
        head, sample = next(rows, []), next(rows, [])
        matches = sum(bool(FIELDS.search(v)) for v in head)
        structurally_valid = len(head) >= 3 and len(head) == len(sample)
        hwinfo_like = len(head) >= 10 and matches >= 6
        sensor_like = matches >= 2 and bool(NAME.search(path.name))
        result.update({"columns": len(head), "sample_columns": len(sample),
                       "sensor_fields": matches,
                       "csv_sensor_evidence": bool(structurally_valid and (hwinfo_like or sensor_like))})
        return result
    except (OSError, csv.Error, UnicodeError, ValueError) as exc:
        return {"path": str(path), "read_error": type(exc).__name__}

def hwinfo_process():
    if os.name != "nt":
        return {"checked": False, "image_names": []}
    try:
        r = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True,
                           text=True, timeout=8)
        names = sorted({row[0] for row in csv.reader(io.StringIO(r.stdout))
                        if row and "hwinfo" in row[0].casefold()})
        return {"checked": r.returncode == 0, "image_names": names}
    except (OSError, subprocess.TimeoutExpired):
        return {"checked": False, "image_names": []}

def scan(places, wait=6, max_results=80):
    found, budget = candidates(places)
    observed = [inspect(path) for path in found]
    observed.sort(key=lambda v: (bool(v.get("csv_sensor_evidence")), v.get("modified_ns", 0)), reverse=True)
    selected = observed[:max_results]
    if wait > 0:
        time.sleep(wait)
    for item in selected:
        try:
            stat = Path(item["path"]).stat()
            item["changed_during_wait"] = (stat.st_size != item.get("bytes") or
                                           stat.st_mtime_ns != item.get("modified_ns"))
            item["grew_during_wait"] = stat.st_size > item.get("bytes", -1)
        except OSError:
            item["changed_during_wait"] = False
            item["grew_during_wait"] = False
        item["live_csv_observed"] = bool(item.get("csv_sensor_evidence") and
                                         item["changed_during_wait"])
    return {"schema": "SOL_SENSOR_LIVE_READONLY_V1",
            "roots_checked": [str(p) for p in places],
            "hwinfo_process": hwinfo_process(), "scan_budget": budget,
            "file_candidates_found": len(found),
            "verified_sensor_csv": sum(bool(x.get("csv_sensor_evidence")) for x in selected),
            "live_sensor_csv_observed": sum(bool(x["live_csv_observed"]) for x in selected),
            "files": selected, "writes": 0, "deletions": 0}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", action="append")
    parser.add_argument("--wait", type=float, default=6)
    args = parser.parse_args()
    print(json.dumps(scan(args.root or roots(), wait=max(args.wait, 0)), ensure_ascii=False, indent=2))
