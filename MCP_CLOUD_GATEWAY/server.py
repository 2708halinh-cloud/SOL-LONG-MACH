"""Read-only SOL MCP gateway bootstrap.

No credentials are embedded. Upstream access is opt-in through environment variables.
"""
from __future__ import annotations

import base64
import json
import os
import secrets
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
import uvicorn

APP_NAME = "SOL MCP Cloud Gateway"
mcp = FastMCP(APP_NAME, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))


def _request(url: str, *, headers: dict[str, str] | None = None, timeout: int = 8) -> tuple[int, Any]:
    req = urllib.request.Request(url, headers=headers or {}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read(1_000_000).decode("utf-8", errors="replace")
            try:
                data: Any = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                data = {"text": raw[:2000]}
            return response.status, data
    except urllib.error.HTTPError as exc:
        raw = exc.read(2000).decode("utf-8", errors="replace")
        return exc.code, {"error": raw}
    except Exception as exc:
        return 0, {"error": type(exc).__name__}


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is not configured")
    return value


def _https_base(name: str) -> str:
    value = _required(name).rstrip("/")
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise RuntimeError(f"{name} must be an HTTPS URL without embedded credentials")
    return value


def _github_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_required('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "SOL-MCP-Cloud-Gateway",
    }


@mcp.tool()
def gateway_status() -> dict[str, Any]:
    """Return gateway configuration presence without revealing secret values."""
    names = (
        "GITHUB_TOKEN", "CHROMA_URL", "AZDO_ORG", "AZDO_PAT",
        "GOOGLE_DRIVE_ACCESS_TOKEN", "LOCAL_BRIDGE_URL", "ANDROID_BRIDGE_URL",
    )
    return {
        "service": APP_NAME,
        "mode": "read-only bootstrap",
        "configured": {name: bool(os.getenv(name, "").strip()) for name in names},
        "mcp_bearer_configured": bool(os.getenv("MCP_BEARER_TOKEN", "").strip()),
        "deployment_is_live": False,
        "note": "Configuration presence is not proof of upstream connectivity.",
    }


@mcp.tool()
def github_repository_readme(owner: str = "2708halinh-cloud", repo: str = "SOL-LONG-MACH") -> dict[str, Any]:
    """Read repository metadata and README from GitHub; no write operations."""
    if not owner.replace("-", "").replace("_", "").isalnum() or not repo.replace("-", "").replace("_", ".").isalnum():
        return {"ok": False, "error": "invalid repository identifier"}
    headers = _github_headers()
    status, meta = _request(f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
    if status != 200:
        return {"ok": False, "stage": "repository_metadata", "http_status": status, "detail": meta}
    readme_status, readme = _request(
        f"https://api.github.com/repos/{owner}/{repo}/readme",
        headers={**headers, "Accept": "application/vnd.github.raw+json"},
    )
    # Avoid returning huge repository content to MCP clients.
    return {
        "ok": True,
        "repository": meta.get("full_name"),
        "default_branch": meta.get("default_branch"),
        "private": meta.get("private"),
        "readme_http_status": readme_status,
        "readme": readme if isinstance(readme, dict) else str(readme)[:5000],
    }


@mcp.tool()
def chroma_heartbeat() -> dict[str, Any]:
    """Read-only Chroma heartbeat; reports configuration or HTTP receipt."""
    try:
        base = _https_base("CHROMA_URL")
    except RuntimeError as exc:
        return {"ok": False, "state": "NEEDS_CONFIGURATION", "detail": str(exc)}
    status, data = _request(f"{base}/api/v2/heartbeat")
    return {"ok": status == 200, "http_status": status, "receipt": data}


@mcp.tool()
def azure_devops_list_projects() -> dict[str, Any]:
    """List Azure DevOps projects using a read-scoped PAT; no mutations."""
    try:
        org = _required("AZDO_ORG")
        pat = _required("AZDO_PAT")
    except RuntimeError as exc:
        return {"ok": False, "state": "NEEDS_CONFIGURATION", "detail": str(exc)}
    if "/" in org or "://" in org:
        return {"ok": False, "error": "AZDO_ORG must be an organization name"}
    token = base64.b64encode((":" + pat).encode()).decode()
    status, data = _request(
        f"https://dev.azure.com/{urllib.parse.quote(org, safe='')}/_apis/projects?api-version=7.1",
        headers={"Authorization": f"Basic {token}", "Accept": "application/json"},
    )
    if status != 200:
        return {"ok": False, "http_status": status, "receipt": data}
    return {"ok": True, "count": data.get("count"), "projects": [
        {"id": p.get("id"), "name": p.get("name"), "state": p.get("state")}
        for p in data.get("value", [])
    ]}


@mcp.tool()
def google_drive_list_files(page_size: int = 10) -> dict[str, Any]:
    """List a small page of Drive files via a runtime OAuth access token."""
    token = os.getenv("GOOGLE_DRIVE_ACCESS_TOKEN", "").strip()
    if not token:
        return {"ok": False, "state": "NEEDS_CONFIGURATION", "detail": "GOOGLE_DRIVE_ACCESS_TOKEN is not configured"}
    page_size = max(1, min(int(page_size), 25))
    query = urllib.parse.urlencode({
        "pageSize": str(page_size),
        "fields": "files(id,name,mimeType,modifiedTime,webViewLink)",
        "orderBy": "modifiedTime desc",
    })
    status, data = _request(
        f"https://www.googleapis.com/drive/v3/files?{query}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    if status != 200:
        return {"ok": False, "http_status": status, "receipt": data}
    return {"ok": True, "files": data.get("files", [])}


def _bridge_probe(env_name: str) -> dict[str, Any]:
    try:
        base = _https_base(env_name)
    except RuntimeError as exc:
        return {"ok": False, "state": "NEEDS_CONFIGURATION", "detail": str(exc)}
    status, data = _request(f"{base}/healthz")
    return {"ok": status == 200, "http_status": status, "receipt": data}


@mcp.tool()
def local_bridge_status() -> dict[str, Any]:
    """Probe the existing local bridge health endpoint over a trusted HTTPS route."""
    return _bridge_probe("LOCAL_BRIDGE_URL")


@mcp.tool()
def android_bridge_status() -> dict[str, Any]:
    """Probe an explicitly configured Android bridge; never runs ADB commands."""
    return _bridge_probe("ANDROID_BRIDGE_URL")


class BearerGuardMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/healthz":
            return await call_next(request)
        expected = os.getenv("MCP_BEARER_TOKEN", "").strip()
        if not expected:
            return JSONResponse({"error": "MCP_BEARER_TOKEN is not configured"}, status_code=503)
        supplied = request.headers.get("authorization", "")
        prefix = "Bearer "
        if not supplied.startswith(prefix) or not secrets.compare_digest(supplied[len(prefix):], expected):
            return JSONResponse({"error": "unauthorized"}, status_code=401, headers={"WWW-Authenticate": "Bearer"})
        return await call_next(request)


app = mcp.streamable_http_app()
app.add_middleware(BearerGuardMiddleware)
app.add_route("/healthz", lambda request: JSONResponse({
    "ok": True,
    "service": APP_NAME,
    "transport": "streamable-http",
    "auth": "required for /mcp",
}), methods=["GET"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
