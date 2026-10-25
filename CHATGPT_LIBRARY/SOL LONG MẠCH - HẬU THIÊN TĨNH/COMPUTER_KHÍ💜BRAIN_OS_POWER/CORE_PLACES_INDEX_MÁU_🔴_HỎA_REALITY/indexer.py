#!/usr/bin/env python3
"""Read-only REALITY CORE INDEX of observed checkout paths, not provider/live state."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

CORE_PATH = "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/CORE_PLACES_INDEX_MÁU_🔴_HỎA_REALITY"
SCHEMA = "SOL_REALITY_CORE_INDEX/1.0"
MAX_HASH_BYTES = 2_000_000
EXCLUDE_PARTS = {"__pycache__", ".git", ".venv", "venv", "node_modules", ".pytest_cache", ".DS_Store"}
SENSITIVE = (
    ".env", "token", "secret", "credential", "private_key", "ssh_key",
    "passwd", "password", "oauth", ".pem", ".p12", ".pfx", "auth.json",
)
REQUIRED_ENTRIES = (
    "README.md", "AGENTS.md", "indexer.py", "PUPPETEER_RUNTIME",
    "CHƯƠNG II — THÂN VẬT LÝ", "PUPPETEER_RUNTIME_READBACK_20261015.json",
)


def _excluded(rel: Path) -> bool:
    for part in rel.parts:
        name = part.casefold()
        if part in EXCLUDE_PARTS or any(term in name for term in SENSITIVE):
            return True
    return False


def inventory(repo_root: Path, *, observed_at: str | None = None) -> dict:
    """Enumerate only the REALITY index subtree; never follow symlink targets."""
    root = repo_root.resolve()
    target = root / CORE_PATH
    if not target.is_dir() or target.is_symlink():
        raise ValueError("INDEX_ROOT_MISSING")
    if not target.resolve().is_relative_to(root):
        raise ValueError("INDEX_ROOT_ESCAPES_REPOSITORY")

    records = []
    excluded_count = 0
    for path in sorted(target.rglob("*"), key=lambda v: v.relative_to(root).as_posix()):
        relative = path.relative_to(root)
        local = path.relative_to(target)
        if _excluded(local) or path.is_symlink():
            excluded_count += 1
            continue
        if not path.is_dir() and not path.is_file():
            continue
        item = {"path": relative.as_posix(),
                "local_path": local.as_posix(),
                "provider": "REPOSITORY_CHECKOUT",
                "kind": "directory" if path.is_dir() else "file"}
        if path.is_file():
            size = path.stat().st_size
            item["size_bytes"] = size
            item["sha256"] = (hashlib.sha256(path.read_bytes()).hexdigest()
                              if size <= MAX_HASH_BYTES else None)
            item["readback_scope"] = ("BYTES_HASHED" if size <= MAX_HASH_BYTES
                                      else "METADATA_ONLY_SIZE_LIMIT")
        records.append(item)
    found = {x["local_path"] for x in records}
    missing = [name for name in REQUIRED_ENTRIES if name not in found]
    stamp = observed_at or datetime.now(timezone.utc).isoformat()
    return {
        "schema": SCHEMA, "observed_at": stamp,
        "source": "LOCAL_CHECKOUT_ONLY_NOT_NATIVE_LIBRARY_OR_LIVE_PROVIDER",
        "root_relative": CORE_PATH, "records": records,
        "excluded_entries": excluded_count, "required_missing": missing,
        "index_operational": not missing,
        "next_action": ("INSPECT_MISSING_INDEX_SOURCE" if missing
                        else "FOLLOW_SOURCE_POINTER_AND_READ_TARGET"),
        "file_count": sum(x["kind"] == "file" for x in records),
        "directory_count": sum(x["kind"] == "directory" for x in records),
    }


def markdown(data: dict) -> str:
    lines = [
        "# REALITY INDEX — observed checkout snapshot",
        "",
        f"Source: `{data['source']}`",
        f"Observed at: `{data['observed_at']}`",
        f"Files: {data['file_count']} | Directories: {data['directory_count']}",
        f"Required missing: {', '.join(data['required_missing']) or 'none'}",
        "",
        "| Kind | Local path | SHA256 / scope |",
        "| --- | --- | --- |",
    ]
    for x in data["records"]:
        suffix = (x.get("sha256") or x.get("readback_scope") or "DIRECTORY")
        lines.append(f"| {x['kind']} | `{x['local_path']}` | `{suffix}` |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only REALITY file INDEX, no writes")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--check", action="store_true",
                        help="exit 2 if required files or paths are missing")
    args = parser.parse_args()
    result = inventory(args.repo_root)
    if args.format == "markdown":
        print(markdown(result), end="")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not args.check or result["index_operational"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
