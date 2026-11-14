#!/usr/bin/env python3
"""Add PostHog MCP to a user-selected JSON MCP config without handling credentials.

Only writes to a target on explicit --apply. No network, OAuth/token export,
workspace discovery, Temp or /mnt/data staging. Write and backup are siblings.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
import pathlib
import sys

POSTHOG = {"type": "http", "url": "https://mcp.posthog.com/mcp"}


def run() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="Existing user-owned MCP JSON config")
    parser.add_argument("--apply", action="store_true", help="Apply the one-entry edit (otherwise inspect only)")
    args = parser.parse_args()
    path = pathlib.Path(args.config).expanduser()
    if not path.is_file():
        print("NOT_FOUND: supplied existing configuration is unavailable", file=sys.stderr)
        return 2
    if str(path).startswith(("/mnt/data", "/tmp", "/var/tmp")):
        print("DENIED: use a persistent, user-owned project directory", file=sys.stderr)
        return 3
    current_bytes = path.read_bytes()
    doc = json.loads(current_bytes.decode("utf-8-sig"))
    if not isinstance(doc, dict):
        raise ValueError("Expected a JSON object")
    key = "mcpServers" if "mcpServers" in doc else "servers" if "servers" in doc else None
    if key is None or not isinstance(doc[key], dict):
        raise ValueError("Missing MCP server registry (mcpServers/servers)")
    old = doc[key].get("posthog")
    if old is not None and old != POSTHOG:
        print("CONFLICT: PostHog entry already exists with different configuration; no overwrite")
        return 4
    if old == POSTHOG:
        print("ALREADY_CONFIGURED: posthog entry matches official endpoint")
        return 0
    if not args.apply:
        print("READY_TO_ATTACH: PostHog endpoint verified in staged config; run with --apply to update this file")
        return 0
    doc[key]["posthog"] = POSTHOG
    body = (json.dumps(doc, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = path.with_name(path.name + ".before-posthog-" + stamp + ".bak")
    stage = path.with_name(path.name + ".posthog-next")
    if backup.exists() or stage.exists():
        print("CONFLICT: sibling backup/staging file already exists", file=sys.stderr)
        return 5
    with backup.open("xb") as fp:
        fp.write(current_bytes)
    with stage.open("xb") as fp:
        fp.write(body)
    os.replace(stage, path)
    check = json.loads(path.read_text(encoding="utf-8"))
    if check[key]["posthog"] != POSTHOG:
        raise RuntimeError("READBACK_FAILED")
    print("CONFIGURED_READBACK_OK: posthog endpoint added; live OAuth and tool access must be verified separately")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
