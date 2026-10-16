#!/usr/bin/env python3
"""Browse and validate the source-specified Azure DevOps MCP toolset (read-only)."""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "TOOLSET_INDEX.json"
SOURCE = ROOT / "docs" / "TOOLSET.md"


def parse_source(text):
    category = ""
    routes = []
    for line in text.splitlines():
        header = re.match(r"^###\s+(.+?)\s*$", line)
        if header:
            category = header.group(1)
            continue
        if not re.match(r"^\|\s*\[[^\]]+\]\(#[^)]*\)", line):
            continue
        cells = [cell.strip() for cell in line[1:-1].split("|")]
        tool = re.fullmatch(r"\[([^\]]+)\]\(#[^)]*\)", cells[0])
        if tool is None or len(cells) not in (2, 3):
            raise ValueError("Unrecognized toolset row: " + line)
        action = (cells[1].strip(chr(96)) or None) if len(cells) == 3 else None
        routes.append({
            "category": category,
            "tool": tool.group(1),
            "action": action,
            "description": cells[-1],
        })
    return routes


def main():
    parser = argparse.ArgumentParser(description="Azure DevOps MCP toolset index (no network calls)")
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list")
    listing.add_argument("--category", default="")
    show = commands.add_parser("show")
    show.add_argument("tool")
    find = commands.add_parser("find")
    find.add_argument("query")
    commands.add_parser("categories")
    commands.add_parser("verify")
    args = parser.parse_args()

    index = json.loads(INDEX.read_text(encoding="utf-8"))
    routes = index["entries"]
    if args.command == "verify":
        parsed = parse_source(SOURCE.read_text(encoding="utf-8"))
        counts_match = (
            index["route_count"] == len(routes)
            and index["tool_count"] == len({r["tool"] for r in routes})
            and index["category_count"] == len({r["category"] for r in routes})
        )
        matched = parsed == routes
        result = {
            "status": "PASS" if matched and counts_match else "FAIL",
            "source_routes": len(parsed),
            "indexed_routes": len(routes),
            "unique_tools": len({r["tool"] for r in routes}),
            "categories": len({r["category"] for r in routes}),
            "source_equals_index": matched,
            "counts_match": counts_match,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if matched and counts_match else 1

    if args.command == "categories":
        result = [
            {"category": c, "routes": sum(r["category"] == c for r in routes)}
            for c in index["category_order"]
        ]
    elif args.command == "show":
        result = [r for r in routes if r["tool"] == args.tool]
    elif args.command == "find":
        query = args.query.casefold()
        result = [
            r for r in routes
            if any(query in str(v).casefold() for v in r.values() if v is not None)
        ]
    else:
        result = [
            r for r in routes
            if not args.category or r["category"].casefold() == args.category.casefold()
        ]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.command in ("show", "find") and not result:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
