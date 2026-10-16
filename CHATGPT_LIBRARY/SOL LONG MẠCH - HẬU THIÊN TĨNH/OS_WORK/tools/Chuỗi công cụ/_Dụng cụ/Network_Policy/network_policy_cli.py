#!/usr/bin/env python3
"""Explicit CLI for policy summary, evaluation, and short-lived TCP checks.

No DNS lookup for a host without an allow-name match. `connect` requires an
explicit policy file plus --execute; it never starts a listening service.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from network_policy import NetworkPolicyError, connect, evaluate, load_policy, summary


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--policy", type=Path, help="UTF-8 JSON policy; omitted => deny all")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("summary", help="Show effective policy without DNS or TCP")
    check = sub.add_parser("evaluate", help="Evaluate a host; allowed DNS names can resolve")
    check.add_argument("host")
    check.add_argument("--no-dns", action="store_true", help="Evaluate name rules without DNS lookup")
    conn = sub.add_parser("connect", help="Explicitly probe a single authorized TCP endpoint")
    conn.add_argument("host")
    conn.add_argument("port", type=int)
    conn.add_argument("--timeout", type=float, default=3.0)
    conn.add_argument("--execute", action="store_true", help="Required opt-in for a real TCP attempt")
    args = p.parse_args(argv)
    try:
        policy = load_policy(args.policy)
        if args.command == "summary":
            result = summary(policy)
        elif args.command == "evaluate":
            result = evaluate(args.host, policy, resolve_dns=not args.no_dns)
        else:
            if args.policy is None:
                raise NetworkPolicyError("connect requires an explicit --policy file")
            if not args.execute:
                raise NetworkPolicyError("connect requires --execute")
            if isinstance(args.port, bool) or not 1 <= args.port <= 65535:
                raise NetworkPolicyError("port must be between 1 and 65535")
            if not 0 < args.timeout <= 30:
                raise NetworkPolicyError("timeout must be > 0 and <= 30 seconds")
            result = connect(args.host, args.port, args.timeout, policy)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (NetworkPolicyError, PermissionError) as exc:
        print(json.dumps({"error": type(exc).__name__, "details": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
