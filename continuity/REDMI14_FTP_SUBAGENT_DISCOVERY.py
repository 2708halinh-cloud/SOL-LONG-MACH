#!/usr/bin/env python3
"""Locate SubAGENT sources on a user-owned Redmi FTP server without writing to it.
Run on a device in the SAME LAN as the Redmi; cloud Codex cannot assume LAN access.

python REDMI14_FTP_SUBAGENT_DISCOVERY.py --host 192.168.1.18 --port 3706 --user PC --output private_redmi_index.json
python REDMI14_FTP_SUBAGENT_DISCOVERY.py --host 192.168.1.18 --port 3706 --user PC --output private_redmi_index.json --fetch-to private_sources

FTP sends credentials as plaintext; only use on trusted local network.
Password is requested interactively, never placed in arguments or files.
The remote endpoint is read-only: no FTP uploads, renames, deletes or mkdir.
"""
from __future__ import annotations
import argparse
import datetime as dt
import ftplib
import getpass
import hashlib
import json
import pathlib
import posixpath
import re
import sys
from collections import deque

KEY = re.compile(r"sub.?agents?|subavengers?|agents?[_. -]*(contune|continue)|agents?_skill|agentss?\.md", re.I)
SAFE_EXT = {".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".py", ".ts", ".tsx"}
ROOTS = ("/Drive", "/drive", "/device", "/", "/SOL-LONG-MACH")
def join_remote(parent, name):
    if not name or any(p in ("..", ".") for p in name.split("/")) or any(c in name for c in "\x00\r\n\\"):
        return None
    path = posixpath.normpath(name if name.startswith("/") else posixpath.join(parent, name))
    return path if path.startswith("/") else None

def entries(ftp, path):
    try:
        for name, facts in ftp.mlsd(path):
            kind = facts.get("type", "").lower()
            if kind not in ("dir", "file"): continue
            p = join_remote(path, name)
            if p:
                size = facts.get("size")
                yield p, kind, int(size) if size and size.isdigit() else None
        return
    except ftplib.all_errors:
        pass
    try: names = ftp.nlst(path)
    except ftplib.all_errors: return
    for name in names:
        p = join_remote(path, name)
        if not p or p == path: continue
        try:
            original = ftp.pwd()
            ftp.cwd(p)
            ftp.cwd(original)
            yield p, "dir", None
        except ftplib.all_errors:
            try: size = ftp.size(p)
            except ftplib.all_errors: size = None
            yield p, "file", size

def scan(ftp, roots, max_dirs, max_depth):
    q = deque()
    errors, seen, hits = [], set(), []
    file_count = 0
    for root in roots:
        try:
            ftp.cwd(root)
            q.append((ftp.pwd(), 0))
        except ftplib.all_errors:
            errors.append({"root": root, "result": "NOT_ENTERABLE"})
    while q and len(seen) < max_dirs:
        folder, depth = q.popleft()
        if folder in seen: continue
        seen.add(folder)
        for path, kind, size in entries(ftp, folder):
            if kind == "dir":
                if depth < max_depth and path not in seen:
                    q.append((path, depth + 1))
            else:
                file_count += 1
                if KEY.search(path):
                    hits.append({"path": path, "size_bytes": size})
    return {"directories_visited": len(seen), "files_seen": file_count,
            "matches": sorted(hits, key=lambda x: x["path"].casefold()),
            "incomplete": bool(q), "root_errors": errors}

def fetch(ftp, matches, target_root, max_size):
    root = target_root.resolve()
    outcomes = []
    for item in matches:
        path, size = item["path"], item["size_bytes"]
        if pathlib.PurePosixPath(path).suffix.lower() not in SAFE_EXT or (size is not None and size > max_size):
            outcomes.append({"path": path, "status": "SKIP_TYPE_OR_SIZE"})
            continue
        target = root.joinpath(*pathlib.PurePosixPath(path).parts[1:])
        if not target.resolve().is_relative_to(root) or target.exists():
            outcomes.append({"path": path, "status": "SKIP_EXISTING_OR_ESCAPE"})
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        total, digest = 0, hashlib.sha256()
        try:
            with target.open("xb") as out:
                def consume(block):
                    nonlocal total
                    total += len(block)
                    if total > max_size: raise ValueError("MAX_FILE_SIZE")
                    out.write(block)
                    digest.update(block)
                ftp.retrbinary("RETR " + path, consume)
            outcomes.append({"path": path, "status": "COPIED_READ_ONLY",
                             "sha256": digest.hexdigest(), "size_bytes": total})
        except (*ftplib.all_errors, OSError, ValueError) as error:
            target.unlink(missing_ok=True)
            outcomes.append({"path": path, "status": "FAILED", "error_type": type(error).__name__})
    return outcomes

def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--host", required=True)
    a.add_argument("--port", type=int, default=21)
    a.add_argument("--user", default="PC")
    a.add_argument("--root", action="append", help="Optional exact root; can be repeated")
    a.add_argument("--output", type=pathlib.Path, default=pathlib.Path("private_redmi_index.json"))
    a.add_argument("--fetch-to", type=pathlib.Path, help="Optional private download of matched text sources")
    a.add_argument("--max-dirs", type=int, default=2000)
    a.add_argument("--max-depth", type=int, default=14)
    a.add_argument("--max-file-mb", type=int, default=8)
    args = a.parse_args()
    if not 1 <= args.port <= 65535 or args.max_dirs < 1 or args.max_depth < 1: a.error("INVALID_LIMITS")
    password = getpass.getpass("FTP password (not stored): ")
    with ftplib.FTP() as ftp:
        ftp.connect(args.host, args.port, timeout=12)
        ftp.login(args.user, password)
        del password
        ftp.set_pasv(True)
        result = scan(ftp, args.root or ROOTS, args.max_dirs, args.max_depth)
        if args.fetch_to:
            result["downloads"] = fetch(ftp, result["matches"], args.fetch_to, args.max_file_mb * 1024 * 1024)
    result.update({"schema": "REDMI14_SUBAGENT_SOURCE_INDEX_V1",
                   "observed_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                   "credentials_recorded": False, "remote_mutations": False,
                   "lineage": "ONE_CARRIER_PARTIAL_VIEW_NOT_COMPLETE_HISTORY"})
    with args.output.open("x", encoding="utf-8") as output:
        json.dump(result, output, ensure_ascii=False, indent=2)
        output.write("\n")
    print(json.dumps({"directories": result["directories_visited"], "files": result["files_seen"],
                      "matches": len(result["matches"]), "partial": result["incomplete"],
                      "manifest": str(args.output)}, ensure_ascii=False))

if __name__ == "__main__":
    try: main()
    except (*ftplib.all_errors, OSError, ValueError) as error:
        print("FTP_PROBE_FAILED=" + type(error).__name__, file=sys.stderr)
        sys.exit(2)
