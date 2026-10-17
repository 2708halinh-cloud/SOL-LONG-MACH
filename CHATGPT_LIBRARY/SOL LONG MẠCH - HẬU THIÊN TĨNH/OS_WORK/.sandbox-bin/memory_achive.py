#!/usr/bin/env python3
"""SOL MEMORY_ACHIVE: explicit-target archive operations; source-first, no auto-execution."""
from __future__ import annotations

import argparse
import bz2
import gzip
import hashlib
import json
import lzma
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import shutil
import stat
import subprocess
import sys
import tarfile
import zipfile

FORMATS = ("ALL", "7Z", "BZ2", "GZ", "JAR", "LR", "RAR", "TAR", "XZ", "ZIP")
STREAMS = {"GZ": gzip, "BZ2": bz2, "XZ": lzma}
NATIVE = {"ZIP", "JAR", "TAR", *STREAMS}
MAX_ITEMS = 10_000
MAX_UNPACKED = 256 * 1024 * 1024
CHUNK = 1024 * 1024
SOUL = (Path(__file__).resolve().parents[2]
        / "COMPUTER_KHÍ💜BRAIN_OS_POWER"
        / "MEMORY_ARCHIVE_THỊT🟠THỔ_SOUL")


class ArchiveError(Exception):
    pass


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for buf in iter(lambda: f.read(CHUNK), b""):
            h.update(buf)
    return h.hexdigest()


def detect(source: Path) -> str:
    """Signature first; compound TAR detection and JAR suffix require valid containers."""
    source = Path(source)
    if not source.is_file() or source.is_symlink():
        raise ArchiveError("SOURCE_NOT_REGULAR_FILE")
    with source.open("rb") as f:
        magic = f.read(16)
    if zipfile.is_zipfile(source):
        return "JAR" if source.suffix.lower() == ".jar" else "ZIP"
    if magic.startswith(bytes.fromhex("377abcaf271c")):
        return "7Z"
    if magic.startswith(b"Rar!\x1a\x07"):
        return "RAR"
    if magic.startswith(b"LRZI"):
        return "LR"
    if magic.startswith(b"\x1f\x8b"):
        return "TAR" if tarfile.is_tarfile(source) else "GZ"
    if magic.startswith(b"BZh"):
        return "TAR" if tarfile.is_tarfile(source) else "BZ2"
    if magic.startswith(bytes.fromhex("fd377a585a00")):
        return "TAR" if tarfile.is_tarfile(source) else "XZ"
    try:
        if tarfile.is_tarfile(source):
            return "TAR"
    except (tarfile.TarError, EOFError, OSError):
        pass
    return "UNKNOWN"


def validate_member(name: str) -> Path:
    if not name or "\x00" in name or "\\" in name:
        raise ArchiveError("UNSAFE_MEMBER_PATH")
    p = PurePosixPath(name)
    w = PureWindowsPath(name)
    if p.is_absolute() or w.is_absolute() or w.drive or ":" in name:
        raise ArchiveError("UNSAFE_MEMBER_PATH")
    if any(x in {"", ".", ".."} for x in name.rstrip("/").split("/")):
        raise ArchiveError("UNSAFE_MEMBER_PATH")
    return Path(*p.parts)


def safe_entries(archive: Path, fmt: str):
    entries = []
    if fmt in {"ZIP", "JAR"}:
        with zipfile.ZipFile(archive) as z:
            for item in z.infolist():
                mode = item.external_attr >> 16
                if stat.S_ISLNK(mode):
                    raise ArchiveError("UNSAFE_ARCHIVE_LINK")
                entries.append((item.filename, item.file_size, item.is_dir()))
    elif fmt == "TAR":
        with tarfile.open(archive, mode="r:*") as t:
            for item in t.getmembers():
                if not (item.isfile() or item.isdir()):
                    raise ArchiveError("UNSAFE_ARCHIVE_TYPE")
                entries.append((item.name, item.size, item.isdir()))
    else:
        raise ArchiveError("LIST_NEEDS_ADAPTER")
    if len(entries) > MAX_ITEMS:
        raise ArchiveError("ENTRY_LIMIT")
    total = 0
    seen = set()
    for name, size, is_dir in entries:
        rel = validate_member(name)
        key = str(rel).casefold()
        if key in seen:
            raise ArchiveError("DUPLICATE_MEMBER")
        seen.add(key)
        total += size
        if total > MAX_UNPACKED:
            raise ArchiveError("UNPACKED_SIZE_LIMIT")
    return entries


def stream_copy(src, dst, *, limit=MAX_UNPACKED):
    total = 0
    while True:
        chunk = src.read(CHUNK)
        if not chunk:
            return total
        total += len(chunk)
        if total > limit:
            raise ArchiveError("UNPACKED_SIZE_LIMIT")
        if dst is not None:
            dst.write(chunk)


def adapter(fmt: str):
    names = {
        "7Z": ("7zz", "7z", "7za"),
        "RAR": ("unrar", "7zz", "7z"),
        "LR": ("lrzip",),
    }
    return next((shutil.which(n) for n in names.get(fmt, ()) if shutil.which(n)), None)


def external_test(archive: Path, fmt: str):
    exe = adapter(fmt)
    if exe is None:
        raise ArchiveError("NEEDS_ADAPTER")
    name = Path(exe).name.lower()
    if fmt == "LR":
        args = [exe, "-t", str(archive)]
    elif name == "unrar":
        args = [exe, "t", "-inul", str(archive)]
    else:
        args = [exe, "t", str(archive)]
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=120, check=False)
    except subprocess.TimeoutExpired as exc:
        raise ArchiveError("ADAPTER_TIMEOUT") from exc
    if p.returncode:
        raise ArchiveError("ADAPTER_TEST_FAILED")
    return name


def test_archive(archive: Path):
    fmt = detect(archive)
    if fmt == "UNKNOWN":
        raise ArchiveError("UNKNOWN_FORMAT")
    if fmt in {"ZIP", "JAR"}:
        safe_entries(archive, fmt)
        with zipfile.ZipFile(archive) as z:
            try:
                bad = z.testzip()
            except RuntimeError as exc:
                raise ArchiveError("ENCRYPTED_OR_UNSUPPORTED") from exc
            if bad:
                raise ArchiveError("CRC_MISMATCH")
    elif fmt == "TAR":
        entries = safe_entries(archive, fmt)
        with tarfile.open(archive, mode="r:*") as t:
            for member in t.getmembers():
                if member.isfile():
                    f = t.extractfile(member)
                    if f is None:
                        raise ArchiveError("MISSING_MEMBER")
                    with f:
                        stream_copy(f, None)
    elif fmt in STREAMS:
        with STREAMS[fmt].open(archive, "rb") as f:
            stream_copy(f, None)
    else:
        external_test(archive, fmt)
    return {"status": "PASS", "format": fmt, "sha256": sha256(archive)}


def list_archive(archive: Path):
    fmt = detect(archive)
    if fmt in {"ZIP", "JAR", "TAR"}:
        entries = safe_entries(archive, fmt)
        return {"format": fmt, "members": [
            {"path": name, "bytes": size, "directory": is_dir}
            for name, size, is_dir in entries]}
    if fmt in STREAMS or fmt == "LR":
        if fmt == "LR" and not adapter(fmt):
            raise ArchiveError("NEEDS_ADAPTER")
        return {"format": fmt, "members": [
            {"path": archive.name, "bytes": None, "stream": True}]}
    if fmt in {"7Z", "RAR"}:
        exe = adapter(fmt)
        if not exe:
            raise ArchiveError("NEEDS_ADAPTER")
        name = Path(exe).name.lower()
        args = ([exe, "lb", str(archive)] if name == "unrar"
                else [exe, "l", "-slt", str(archive)])
        p = subprocess.run(args, capture_output=True, text=True, timeout=120, check=False)
        if p.returncode:
            raise ArchiveError("ADAPTER_LIST_FAILED")
        return {"format": fmt, "adapter": name, "listing": p.stdout[:20_000]}
    raise ArchiveError("UNKNOWN_FORMAT")


def _inputs(paths):
    items = []
    names = set()
    for src in map(Path, paths):
        if src.is_symlink() or not src.exists():
            raise ArchiveError("UNSAFE_INPUT")
        walk = [src] + sorted(src.rglob("*")) if src.is_dir() else [src]
        for part in walk:
            if part.is_symlink() or not (part.is_file() or part.is_dir()):
                raise ArchiveError("UNSAFE_INPUT")
            name = (Path(src.name) / part.relative_to(src)).as_posix()
            validate_member(name)
            if name.casefold() in names:
                raise ArchiveError("DUPLICATE_INPUT")
            names.add(name.casefold())
            items.append((part, name))
    if len(items) > MAX_ITEMS:
        raise ArchiveError("ENTRY_LIMIT")
    if sum(p.stat().st_size for p, _ in items if p.is_file()) > MAX_UNPACKED:
        raise ArchiveError("INPUT_SIZE_LIMIT")
    return items


def pack(paths, fmt: str, output: Path):
    if fmt not in FORMATS or fmt == "ALL":
        raise ArchiveError("UNKNOWN_FORMAT")
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise ArchiveError("OUTPUT_EXISTS")
    if not output.parent.is_dir():
        raise ArchiveError("OUTPUT_PARENT_MISSING")
    items = _inputs(paths)
    if fmt in STREAMS:
        if len(items) != 1 or not items[0][0].is_file():
            raise ArchiveError("STREAM_REQUIRES_ONE_FILE")
        with items[0][0].open("rb") as src, STREAMS[fmt].open(output, "xb") as dst:
            shutil.copyfileobj(src, dst, CHUNK)
    elif fmt in {"ZIP", "JAR"}:
        with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as z:
            for path, name in items:
                if path.is_dir():
                    z.writestr(name + "/", b"")
                else:
                    z.write(path, name)
    elif fmt == "TAR":
        with tarfile.open(output, "x") as t:
            for path, name in items:
                t.add(path, arcname=name, recursive=False)
    elif fmt in {"7Z", "RAR", "LR"}:
        exe = adapter(fmt)
        if not exe or (fmt == "RAR" and Path(exe).name.lower() != "rar"):
            raise ArchiveError("PACK_NEEDS_ADAPTER")
        if fmt == "LR":
            if len(items) != 1 or not items[0][0].is_file():
                raise ArchiveError("STREAM_REQUIRES_ONE_FILE")
            args = [exe, "-o", str(output.absolute()), str(items[0][0].absolute())]
        else:
            args = [exe, "a", str(output.absolute()), *[str(Path(p).absolute()) for p in paths]]
        p = subprocess.run(args, capture_output=True, text=True, timeout=120, check=False)
        if p.returncode:
            raise ArchiveError("PACK_ADAPTER_FAILED")
    return test_archive(output)


def unpack(archive: Path, destination: Path):
    archive, destination = Path(archive), Path(destination)
    fmt = detect(archive)
    if destination.exists() or destination.is_symlink():
        raise ArchiveError("DESTINATION_EXISTS")
    if not destination.parent.is_dir():
        raise ArchiveError("DESTINATION_PARENT_MISSING")
    test_archive(archive)
    if fmt in {"7Z", "RAR"}:
        # External extractors are not trusted with unvalidated links or paths.
        raise ArchiveError("SAFE_EXTRACT_HANDLER_REQUIRED")
    destination.mkdir()
    if fmt in STREAMS or fmt == "LR":
        name = archive.name
        if fmt in STREAMS:
            name = name.rsplit(".", 1)[0]
            with STREAMS[fmt].open(archive, "rb") as src, (destination / name).open("xb") as dst:
                stream_copy(src, dst)
        else:
            name = archive.stem
            exe = adapter("LR")
            p = subprocess.run([exe, "-d", "-o", str(destination / name), str(archive)],
                               capture_output=True, text=True, timeout=120, check=False)
            if p.returncode:
                raise ArchiveError("LRZIP_EXTRACT_FAILED")
    elif fmt in {"ZIP", "JAR"}:
        with zipfile.ZipFile(archive) as z:
            for info in z.infolist():
                path = destination / validate_member(info.filename)
                if info.is_dir():
                    path.mkdir(parents=True, exist_ok=True)
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with z.open(info) as src, path.open("xb") as dst:
                        stream_copy(src, dst)
    elif fmt == "TAR":
        with tarfile.open(archive, mode="r:*") as t:
            for info in t.getmembers():
                path = destination / validate_member(info.name)
                if info.isdir():
                    path.mkdir(parents=True, exist_ok=True)
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with t.extractfile(info) as src, path.open("xb") as dst:
                        stream_copy(src, dst)
    return {"status": "PASS", "destination": str(destination),
            "source_sha256": sha256(archive),
            "readback": sorted(({"path": p.relative_to(destination).as_posix(), "sha256": sha256(p)}
                               for p in destination.rglob("*") if p.is_file()), key=lambda x: x["path"])}


def inventory(root: Path):
    root = Path(root)
    if not root.is_dir():
        raise ArchiveError("ROOT_NOT_FOUND")
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            continue
        if path.is_file():
            fmt = detect(path)
            if fmt != "UNKNOWN":
                rows.append({"source_path": path.relative_to(root).as_posix(),
                             "archive_format": fmt,
                             "size_bytes": path.stat().st_size,
                             "sha256": sha256(path)})
    return {"status": "PASS", "root": str(root), "count": len(rows), "items": rows}


def main(argv=None):
    p = argparse.ArgumentParser(description="SOUL archive carrier, no implicit writes")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("formats")
    for command in ("detect", "list", "test"):
        sub.add_parser(command).add_argument("archive", type=Path)
    sub.add_parser("inventory").add_argument("root", type=Path)
    q = sub.add_parser("pack")
    q.add_argument("format", choices=FORMATS)
    q.add_argument("output", type=Path)
    q.add_argument("inputs", nargs="+", type=Path)
    q = sub.add_parser("unpack")
    q.add_argument("archive", type=Path)
    q.add_argument("destination", type=Path)
    a = p.parse_args(argv)
    try:
        if a.command == "formats":
            result = {"status": "PASS", "formats": [
                {"name": f, "handler": "internal" if f in NATIVE else adapter(f) or "NEEDS_ADAPTER"}
                for f in FORMATS], "canonical_root": str(SOUL)}
        elif a.command == "detect":
            result = {"format": detect(a.archive)}
        elif a.command == "list":
            result = list_archive(a.archive)
        elif a.command == "test":
            result = test_archive(a.archive)
        elif a.command == "inventory":
            result = inventory(a.root)
        elif a.command == "pack":
            result = pack(a.inputs, a.format, a.output)
        else:
            result = unpack(a.archive, a.destination)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (ArchiveError, OSError, ValueError, EOFError, RuntimeError,
            tarfile.TarError, zipfile.BadZipFile, lzma.LZMAError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
