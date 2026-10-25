#!/usr/bin/env python3
"""Run real, read-only 7Z/RAR/LR fixtures and emit a hash-bound receipt."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "CHATGPT_LIBRARY" / "SOL LONG MẠCH - HẬU THIÊN TĨNH"
          / "OS_WORK" / ".sandbox-bin" / "sol_archive_10_formats.py")
spec = importlib.util.spec_from_file_location("sol_archive_10_formats", SOURCE)
if spec is None or spec.loader is None:
    raise SystemExit("SOURCE_IMPORT_FAILED")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

if len(sys.argv) != 4:
    raise SystemExit("usage: verify_real_archive_fixtures.py REAL_7Z REAL_RAR REAL_LRZIP")

cases = [
    (Path(sys.argv[1]), "7Z", {"7z", "7zz", "7za"}),
    (Path(sys.argv[2]), "RAR", {"unrar"}),
    (Path(sys.argv[3]), "LR", {"lrzip"}),
]
rows = []
for path, expected_format, expected_adapters in cases:
    before = path.read_bytes()
    before_sha = hashlib.sha256(before).hexdigest()
    result = mod.inspect(path)
    after = path.read_bytes()
    row = {
        "fixture": path.name,
        "format": result.get("detected"),
        "status": result.get("status"),
        "adapter": result.get("adapter"),
        "bytes": len(before),
        "sha256_before": before_sha,
        "sha256_reported": result.get("sha256"),
        "sha256_after": hashlib.sha256(after).hexdigest(),
        "source_unchanged": before == after,
        "extraction_performed": result.get("extraction_performed"),
        "sensitive_data_copied": result.get("sensitive_data_copied"),
        "error_code": result.get("error_code"),
    }
    rows.append(row)
    assert row["format"] == expected_format, row
    assert row["status"] == "PASS", row
    assert str(row["adapter"]).lower() in expected_adapters, row
    assert row["sha256_reported"] == before_sha == row["sha256_after"], row
    assert row["source_unchanged"] is True, row
    assert row["extraction_performed"] is False, row
    assert row["sensitive_data_copied"] is False, row

print(json.dumps({
    "schema": "SOL_ARCHIVE_REAL_FIXTURE_READBACK/1.0",
    "fixture_count": len(rows),
    "all_passed": all(row["status"] == "PASS" for row in rows),
    "source_archives_modified": False,
    "extraction_performed": False,
    "fixtures": rows,
}, ensure_ascii=False, sort_keys=True))
