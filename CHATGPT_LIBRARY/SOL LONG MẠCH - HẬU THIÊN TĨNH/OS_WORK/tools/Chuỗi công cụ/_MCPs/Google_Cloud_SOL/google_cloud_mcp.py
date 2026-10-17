#!/usr/bin/env python3
"""Google Cloud local, read-only MCP over stdio. Uses installed gcloud CLI user identity.

Zero external Python dependencies. No tokens are read or printed by this server.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
from typing import Any

PROJECT_RE = re.compile(r"^[a-z][a-z0-9-]{4,61}[a-z0-9]$")
PROJECT_DEFAULT = "alert-tiger-508618-h7"
SERVER_NAME = "Google Cloud"
SERVER_VERSION = "0.1.0"
TOOLS: list[dict[str, Any]] = [
    {"name": "gcp_status", "description": "Check local gcloud CLI presence, project selection and whether CLI credentials are active. Read-only; never exposes OAuth tokens.", "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "gcp_projects_list", "description": "List accessible Google Cloud projects (read-only).", "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "gcp_project_describe", "description": "Describe the configured Google Cloud project (read-only).", "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "gcp_storage_buckets_list", "description": "List Cloud Storage buckets in the configured project (read-only).", "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "gcp_run_services_list", "description": "List Cloud Run services in the configured project (read-only).", "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "gcp_compute_instances_list", "description": "List Compute Engine VM instances in the configured project (read-only).", "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "gcp_enabled_apis_list", "description": "List enabled Google Cloud APIs in the configured project (read-only).", "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "gcp_usage_analyse", "description": "Analyse user-supplied Google Cloud dashboard metrics offline. Does not call Cloud APIs, retry failures, inspect credentials or assume cost.", "inputSchema": {"type": "object", "properties": {"metrics": {"type": "array", "maxItems": 300, "items": {"type": "object"}}}, "required": ["metrics"], "additionalProperties": False}},
]

def selected_project() -> str:
    p = os.environ.get("SOL_GCP_PROJECT_ID", PROJECT_DEFAULT).strip()
    if not PROJECT_RE.fullmatch(p):
        raise ValueError("Invalid Google Cloud project ID in SOL_GCP_PROJECT_ID")
    return p


def execute_gcloud(arguments: list[str], timeout: int = 40) -> Any:
    binary = shutil.which("gcloud") or shutil.which("gcloud.cmd")
    if not binary:
        raise RuntimeError("Google Cloud CLI (gcloud) is not installed or not in PATH on this Windows host.")
    # Only constant, internally-constructed subcommands are permitted. No arbitrary shell input.
    cmd = [binary, "--quiet", *arguments, "--format=json"]
    try:
        r = subprocess.run(cmd, shell=False, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout,
                           stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired as e:
        raise RuntimeError("gcloud timed out; verify VPN/network and Google OAuth session") from e
    if r.returncode:
        err = (r.stderr or "").strip()
        # Do not echo arbitrary diagnostic dumps or potential credential material.
        if "not authenticated" in err.lower() or "login" in err.lower() or "no credentialed accounts" in err.lower():
            raise RuntimeError("gcloud is not authenticated on the Windows host. Run: gcloud auth login")
        raise RuntimeError(f"gcloud command failed (exit {r.returncode}); verify project access, API enablement and IAM permissions")
    if not r.stdout.strip():
        return []
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        raise RuntimeError("Unexpected non-JSON response from gcloud") from None


def dispatch(name: str, args: dict[str, Any]) -> Any:
    if name not in {t["name"] for t in TOOLS}:
        raise ValueError(f"Unknown tool: {name}")
    if name == "gcp_usage_analyse":
        if not isinstance(args, dict) or set(args) != {"metrics"}:
            raise ValueError("GCP_USAGE_METRICS_REQUIRED")
        source = Path(__file__).with_name("gcp_usage_guard.py")
        spec = importlib.util.spec_from_file_location("sol_gcp_usage_guard", source)
        if spec is None or spec.loader is None:
            raise RuntimeError("GCP_USAGE_GUARD_SOURCE_MISSING")
        guard = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(guard)
        return guard.analyse(args["metrics"])
    if args:
        raise ValueError("This version takes no tool parameters; project is bound by SOL_GCP_PROJECT_ID")
    p = selected_project()
    if name == "gcp_status":
        exists = bool(shutil.which("gcloud") or shutil.which("gcloud.cmd"))
        if not exists:
            return {"project": p, "gcloud_installed": False, "authenticated": False, "host_role": "Windows control plane", "mode": "read_only"}
        try:
            accounts = execute_gcloud(["auth", "list"])
            # gcloud status 'ACTIVE' is current active. Never include email/account data.
            active = any(str(x.get("status", "")).upper() == "ACTIVE" for x in accounts if isinstance(x, dict)) if isinstance(accounts, list) else False
            return {"project": p, "gcloud_installed": True, "authenticated": active, "host_role": "Windows control plane", "mode": "read_only"}
        except Exception:
            return {"project": p, "gcloud_installed": True, "authenticated": False, "host_role": "Windows control plane", "mode": "read_only"}
    if name == "gcp_projects_list":
        # Projects list is scoped to the signed-in user; no forced project.
        return execute_gcloud(["projects", "list"])
    if name == "gcp_project_describe":
        return execute_gcloud(["projects", "describe", p])
    if name == "gcp_storage_buckets_list":
        return execute_gcloud(["storage", "buckets", "list", "--project=" + p])
    if name == "gcp_run_services_list":
        return execute_gcloud(["run", "services", "list", "--project=" + p])
    if name == "gcp_compute_instances_list":
        return execute_gcloud(["compute", "instances", "list", "--project=" + p])
    if name == "gcp_enabled_apis_list":
        return execute_gcloud(["services", "list", "--enabled", "--project=" + p])
    raise AssertionError(name)


def make_response(id_: Any, result: Any = None, error: dict[str, Any] | None = None) -> dict[str, Any]:
    r: dict[str, Any] = {"jsonrpc": "2.0", "id": id_}
    if error is not None:
        r["error"] = error
    else:
        r["result"] = result
    return r


def handle(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method", "")
    if method.startswith("notifications/"):
        return None
    if "id" not in message:
        return None
    request_id = message["id"]
    params = message.get("params") or {}
    try:
        if method == "initialize":
            requested = params.get("protocolVersion", "2025-06-18")
            # Negotiate a tested MCP version instead of advertising unsupported stateless semantics.
            version = requested if requested in ("2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25") else "2025-06-18"
            result = {"protocolVersion": version, "capabilities": {"tools": {"listChanged": False}},
                      "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                      "instructions": "Read-only Google Cloud tools running on Windows via local gcloud CLI. Never return tokens or secrets."}
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            name = params.get("name", "")
            value = dispatch(name, params.get("arguments") or {})
            result = {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}], "isError": False}
        elif method in ("resources/list", "prompts/list"):
            result = {"resources": []} if method == "resources/list" else {"prompts": []}
        else:
            return make_response(request_id, error={"code": -32601, "message": "Method not found"})
        return make_response(request_id, result=result)
    except (RuntimeError, ValueError, TypeError) as e:
        if method == "tools/call":
            return make_response(request_id, result={"content": [{"type": "text", "text": str(e)}], "isError": True})
        return make_response(request_id, error={"code": -32602, "message": str(e)})
    except Exception:
        # Avoid exposing env / accidental secrets in exceptions.
        return make_response(request_id, error={"code": -32603, "message": "Internal error"})


def main() -> None:
    # MCP stdio is newline-delimited JSON-RPC. Never send diagnostics to stdout.
    for raw in sys.stdin.buffer:
        try:
            message = json.loads(raw.decode("utf-8-sig"))
            if not isinstance(message, dict):
                raise ValueError("invalid request")
            response = handle(message)
            if response is not None:
                sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
                sys.stdout.flush()
        except Exception:
            # Invalid JSON has no trustworthy id; a generic error is safe.
            sys.stdout.write(json.dumps(make_response(None, error={"code": -32700, "message": "Parse error"})) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
