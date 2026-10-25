#!/usr/bin/env python3
"""Source-bound cross-environment Core operators inspired by Azure DevOps MCP TOOLSET.md.

Accepts caller-supplied observations. This is NOT an Azure MCP transport, connector,
a proof of platform truth, or a source of implicit access to other accounts.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

SCHEMA = "SOL_MULTIENVIRO_CORE_OBSERVATIONS_V1"
REQUIRED = ("provider", "kind", "stable_id", "name", "source_ref", "observed_at")


def _checked(data):
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError("OBSERVATION_SCHEMA_MISMATCH")
    records = data.get("records")
    if not isinstance(records, list):
        raise ValueError("RECORDS_REQUIRED")
    for item in records:
        if not isinstance(item, dict) or any(not item.get(k) for k in REQUIRED):
            raise ValueError("INCOMPLETE_IDENTITY_OR_PROVENANCE")
        if item["kind"] not in ("project", "project_candidate", "group", "carrier"):
            raise ValueError("UNSUPPORTED_KIND")
        if item["kind"] == "group" and not item.get("parent_id"):
            raise ValueError("GROUP_PARENT_REQUIRED")
    return records


def list_projects(data):
    """Enumerate observed project or candidate records without renaming folders as projects."""
    return [dict(x) for x in _checked(data)
            if x["kind"] in ("project", "project_candidate")]


def list_project_groups(data, *, provider, project_id):
    """Group membership requires an explicit parent identity and provider match."""
    return [dict(x) for x in _checked(data)
            if x["kind"] == "group" and x["provider"] == provider
            and x["parent_id"] == project_id]


def get_identity_ids(data, *, provider=None, stable_id=None, name=None):
    """Exact IDs are scoped to provider. A name match alone never proves identity."""
    records = _checked(data)
    if not stable_id and not name:
        raise ValueError("IDENTITY_FILTER_REQUIRED")
    found = [dict(x) for x in records
             if (provider is None or x["provider"] == provider)
             and (stable_id is None or x["stable_id"] == stable_id)
             and (name is None or x["name"] == name)]
    keys = {(x["provider"], x["kind"], x["stable_id"]) for x in found}
    if not found:
        state = "NO_OBSERVATION"
    elif len(keys) > 1 or (name and not stable_id):
        state = "CANDIDATES_NEED_ID_CONFIRMATION"
    elif len({x.get("revision") for x in found}) > 1:
        state = "HISTORY_MULTIPLE_REVISIONS"
    else:
        state = "SCOPED_ID_OBSERVED_NOT_TRUTH_VERIFIED"
    next_edges = {
        "NO_OBSERVATION": ["FRESH_PROVIDER_SEARCH", "CHECK_OTHER_AUTHORIZED_CARRIERS"],
        "CANDIDATES_NEED_ID_CONFIRMATION": ["QUERY_PROVIDER_IDS", "READ_PARENT_RELATIONS"],
        "HISTORY_MULTIPLE_REVISIONS": ["READ_LATEST_PROVIDER_REVISION", "COMPARE_CAUSAL_DELTAS"],
        "SCOPED_ID_OBSERVED_NOT_TRUTH_VERIFIED": ["READ_PROVIDER_METADATA", "VERIFY_SOURCE_AND_TARGET_READBACK"],
    }
    return {"state": state, "records": found, "provenance_required": True,
            "raw_source_is_not_truth": True,
            "next_callable_edges_to_probe": next_edges[state]}


def main():
    p = argparse.ArgumentParser(description="Offline read-only SOL multi-environment Core")
    p.add_argument("--snapshot", type=Path, required=True,
                   help="A caller-exported local JSON observation file; no provider access")
    p.add_argument("--operation", choices=("projects", "groups", "identity"), required=True)
    p.add_argument("--provider")
    p.add_argument("--project-id")
    p.add_argument("--stable-id")
    p.add_argument("--name")
    args = p.parse_args()
    data = json.loads(args.snapshot.read_text(encoding="utf-8"))
    if args.operation == "projects":
        result = list_projects(data)
    elif args.operation == "groups":
        if not args.provider or not args.project_id:
            p.error("--provider and --project-id required for groups")
        result = list_project_groups(data, provider=args.provider, project_id=args.project_id)
    else:
        result = get_identity_ids(data, provider=args.provider,
                                  stable_id=args.stable_id, name=args.name)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
