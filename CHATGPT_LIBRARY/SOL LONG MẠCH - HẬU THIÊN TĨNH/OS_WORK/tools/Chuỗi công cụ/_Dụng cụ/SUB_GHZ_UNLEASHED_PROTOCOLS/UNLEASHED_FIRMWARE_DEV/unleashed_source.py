#!/usr/bin/env python3
"""Inspect and safely unpack a user-provided Flipper Unleashed source archive.

No firmware build, flashing, RF transmission or network activity is performed.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import zipfile

EXPECTED_SHA256 = "d0c5c75f790695ccc3b3fccb047a72b454d6694683625cc423114581c61be00f"
EXPECTED_FILES_AND_DIRS = 5482
MAX_TOTAL_BYTES = 100_000_000
MAX_MEMBERS = 10_000


def inspect(source):
    source = Path(source)
    digest = hashlib.sha256()
    with source.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    sha = digest.hexdigest()
    with zipfile.ZipFile(source) as archive:
        entries = archive.infolist()
        unsafe = []
        for item in entries:
            name = PurePosixPath(item.filename)
            mode = item.external_attr >> 16
            if (name.is_absolute() or ".." in name.parts or "\\" in item.filename
                    or (mode and stat.S_IFMT(mode) == stat.S_IFLNK)):
                unsafe.append(item.filename)
        size = sum(item.file_size for item in entries)
        crc_error = archive.testzip() if len(entries) <= MAX_MEMBERS and size <= MAX_TOTAL_BYTES else "limits exceeded"
    result = {
        "archive": source.name,
        "sha256": sha,
        "sha256_matches_supplied_archive": sha == EXPECTED_SHA256,
        "members": len(entries),
        "members_match_supplied_archive": len(entries) == EXPECTED_FILES_AND_DIRS,
        "uncompressed_bytes": size,
        "unsafe_paths": unsafe[:20],
        "crc_error": crc_error,
        "source_verified": sha == EXPECTED_SHA256 and not unsafe and not crc_error
            and len(entries) == EXPECTED_FILES_AND_DIRS and size <= MAX_TOTAL_BYTES,
    }
    return result


def extract(source, destination):
    result = inspect(source)
    if not result["source_verified"]:
        raise ValueError("Archive must pass SHA-256, CRC and path checks before extraction")
    destination = Path(destination)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("Extraction destination must be empty")
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with zipfile.ZipFile(source) as archive:
        for item in archive.infolist():
            target = (root / item.filename).resolve()
            if not target.is_relative_to(root):
                raise ValueError("Unsafe destination: " + item.filename)
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(item) as reader, target.open("xb") as writer:
                    shutil.copyfileobj(reader, writer, length=1024 * 1024)
    return {"extracted_to": str(root), "source_verified": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", help="Path to unleashed-firmware-dev.zip")
    parser.add_argument("--extract-to", help="Extract only after full integrity verification")
    args = parser.parse_args()
    try:
        result = extract(args.archive, args.extract_to) if args.extract_to else inspect(args.archive)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("source_verified") else 2
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
