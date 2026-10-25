#!/usr/bin/env python3
"""Master OAth — multi-route MCP auth bridge, credential-free on disk.

Prioritize existing authenticated providers before browser/OAuth fallback.  Do not
store, print, or transmit passwords, Bearer values, cookies, callbacks or OTPs.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import sys
import urllib.error
import urllib.request
import webbrowser
from urllib.parse import urlsplit
from dataclasses import dataclass
from typing import Any

HOSTINGER_MCP_URL = "https://mcp.hostinger.com"
HOSTINGER_LOGIN = "https://auth.hostinger.com/"
CHATGPT_LOGIN = "https://chatgpt.com/"
ALLOWED_PROVIDER = {"hostinger", "gmail", "chatgpt"}
CHATGPT_ACTIONS = {"open", "history_export", "search_conversations"}
HOSTINGER_READ_OPS = {"dns_records_list", "dns_snapshots_list", "domains_forwarding_get"}
MAX_HTTP_BYTES = 2_000_000


class AuthRouteError(Exception):
    pass


def route(provider: str, intent: str, *, connected: bool = False, domain: str = "") -> dict[str, Any]:
    provider = provider.lower().strip()
    if provider not in ALLOWED_PROVIDER:
        raise AuthRouteError("UNSUPPORTED_PROVIDER")
    if provider == "chatgpt":
        if intent not in CHATGPT_ACTIONS:
            raise AuthRouteError("UNSUPPORTED_CHATGPT_ACTION")
        return {"next_agent":"OPEN_CHATGPT_OFFICIAL_BROWSER", "url":CHATGPT_LOGIN,
                "operation":intent, "identity":"PROVIDER_SESSION_ONLY",
                "connected_gmail_is_not_chatgpt_login":True,
                "browser_session_verified":False, "cookie_persistence":"BROWSER_OWNED_ONLY",
                "export_search":"LOCAL_EXPORTED_CONVERSATIONS_AFTER_ACQUISITION",
                "needs_browser":True}
    if provider == "hostinger":
        if intent not in HOSTINGER_READ_OPS:
            raise AuthRouteError("OPERATION_NOT_READONLY_APPROVED")
        if not domain or ":" in domain or "/" in domain or "@" in domain or " " in domain:
            raise AuthRouteError("DOMAIN_REQUIRED")
        if connected:
            return {"next_agent": "CALL_CONNECTED_HOSTINGER_PROVIDER", "operation": intent,
                    "params": {"domain": domain}, "auth": "REUSE_EXISTING_SESSION", "needs_browser": False}
        return {"next_agent": "USE_HOSTINGER_MCP_ENV_OR_APPROVED_BROWSER", "endpoint": HOSTINGER_MCP_URL,
                "operation": intent, "params": {"domain": domain}, "needs_browser": True,
                "browser_login": HOSTINGER_LOGIN, "credentials": "OS_VAULT_OR_IDP_ONLY"}
    if intent not in {"get_profile", "search_emails"}:
        raise AuthRouteError("OPERATION_NOT_READONLY_APPROVED")
    if connected:
        return {"next_agent": "CALL_CONNECTED_GMAIL_PROVIDER", "operation": intent,
                "auth": "REUSE_EXISTING_SESSION", "needs_browser": False}
    return {"next_agent": "CONNECT_OFFICIAL_GMAIL_PROVIDER", "needs_browser": True,
            "credentials": "PROVIDER_CONSENT_UI_ONLY"}


def summarize_dns(zone: Any, domain: str) -> dict[str, Any]:
    """Redact TXT tokens/MX and host targets in durable output; no fabricated LIVE assertions."""
    if isinstance(zone, dict) and "text" in zone:
        zone = json.loads(zone["text"])
    if isinstance(zone, str):
        zone = json.loads(zone)
    if isinstance(zone, dict) and "result" in zone:
        zone = zone["result"]
    if not isinstance(zone, list):
        raise AuthRouteError("DNS_RESPONSE_NOT_A_LIST")
    records = []
    for entry in zone:
        if not isinstance(entry, dict):
            raise AuthRouteError("INVALID_DNS_RECORD")
        name = str(entry.get("name", ""))
        kind = str(entry.get("type", "")).upper()
        targets = entry.get("records", [])
        if not isinstance(targets, list):
            raise AuthRouteError("INVALID_DNS_TARGETS")
        ip_class = ""
        if kind in {"A", "AAAA"}:
            parsed = []
            for target in targets:
                try:
                    value = str(target["content"])
                    address = ipaddress.ip_address(value)
                    parsed.append("private_or_special" if not address.is_global else "global")
                except (KeyError, ValueError, TypeError):
                    parsed.append("unclassified")
            ip_class = "mixed" if len(set(parsed)) > 1 else (parsed[0] if parsed else "")
        records.append({"name": name, "type": kind, "ttl": entry.get("ttl"),
                        "target_count": len(targets), "address_class": ip_class})
    return {"domain": domain, "record_groups": len(records),
            "records": records, "values_redacted": True,
            "caution": "Provider readback only; no DNS mutation and no proof of PC connectivity"}


@dataclass
class RemoteMCP:
    """Minimal Streamable HTTP MCP client for official Hostinger endpoint only.

    Authentication is read from process environment, never from checked-in files.
    No redirects to other hosts; untrusted endpoint substitution not supported.
    """
    bearer: str
    opener: Any = None
    session: str = ""
    request_id: int = 0

    def __post_init__(self) -> None:
        if not self.bearer:
            raise AuthRouteError("MCP_BEARER_ENV_MISSING")
        if self.opener is None:
            self.opener = urllib.request.build_opener(_DenyRedirect())

    def _call(self, method: str, params: dict[str, Any] | None = None, *, notification: bool = False) -> Any:
        req: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if not notification:
            self.request_id += 1
            req["id"] = self.request_id
        if params is not None:
            req["params"] = params
        headers = {"Authorization": "Bearer " + self.bearer, "Content-Type": "application/json",
                   "Accept": "application/json, text/event-stream", "MCP-Protocol-Version": "2025-03-26"}
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        request = urllib.request.Request(HOSTINGER_MCP_URL, data=json.dumps(req).encode("utf-8"),
                                         headers=headers, method="POST")
        try:
            with self.opener.open(request, timeout=18) as response:
                self.session = response.headers.get("Mcp-Session-Id", self.session)
                if notification or response.status == 202:
                    return None
                data = response.read(MAX_HTTP_BYTES + 1)
                if len(data) > MAX_HTTP_BYTES:
                    raise AuthRouteError("MCP_RESPONSE_TOO_LARGE")
                body = data.decode("utf-8")
                media = response.headers.get("Content-Type", "")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            # Do not risk printing response headers/URLs that contain secrets.
            raise AuthRouteError("HOSTINGER_MCP_TRANSPORT_FAILED") from None
        if "text/event-stream" in media:
            frames = [line[5:].strip() for line in body.splitlines() if line.startswith("data:")]
            messages = [json.loads(line) for line in frames if line and line != "[DONE]"]
            matches = [m for m in messages if isinstance(m, dict) and m.get("id") == req.get("id")]
            payload = matches[-1] if matches else (messages[-1] if messages else {})
        else:
            payload = json.loads(body)
        if isinstance(payload, dict) and "error" in payload:
            raise AuthRouteError("MCP_REMOTE_RETURNED_ERROR")
        return payload.get("result") if isinstance(payload, dict) else payload

    def dns(self, domain: str) -> dict[str, Any]:
        route("hostinger", "dns_records_list", connected=True, domain=domain)
        self._call("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                                  "clientInfo": {"name": "Master OAth", "version": "1.0"}})
        self._call("notifications/initialized", notification=True)
        response = self._call("tools/call", {"name": "dns_records_list", "arguments": {"domain": domain}})
        if not isinstance(response, dict) or response.get("isError"):
            raise AuthRouteError("MCP_DNS_TOOL_FAILED")
        text_blocks = [b.get("text", "") for b in response.get("content", []) if b.get("type") == "text"]
        if not text_blocks:
            raise AuthRouteError("MCP_DNS_EMPTY_RESPONSE")
        return summarize_dns(text_blocks[0], domain)


class _DenyRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise AuthRouteError("MCP_REDIRECT_REFUSED")


def browser_target(provider: str, url: str = "") -> str:
    """Official browser entry or an explicitly supplied HTTPS site; no auth-bearing URL."""
    provider = provider.lower().strip()
    if provider == "chatgpt":
        if url and url.rstrip("/") != CHATGPT_LOGIN.rstrip("/"):
            raise AuthRouteError("CHATGPT_URL_NOT_OFFICIAL")
        return CHATGPT_LOGIN
    if provider == "hostinger":
        if url and url.rstrip("/") != HOSTINGER_LOGIN.rstrip("/"):
            raise AuthRouteError("HOSTINGER_URL_NOT_OFFICIAL")
        return HOSTINGER_LOGIN
    if provider == "custom":
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise AuthRouteError("INVALID_BROWSER_ENTRY_URL")
        return url
    raise AuthRouteError("UNSUPPORTED_BROWSER_PROVIDER")


def browser_handoff(provider: str = "chatgpt", *, open_browser: bool = False, url: str = "") -> dict[str, Any]:
    target = browser_target(provider, url)
    opened = bool(webbrowser.open(target)) if open_browser else False
    return {"url":target, "browser_open_attempted":open_browser,
            "browser_open_reported":opened, "logged_in":False,
            "cookie_saved_by_master_oath":False,
            "next_agent":"OBSERVE_PROVIDER_UI_LOGIN_THEN_RETRIEVE_SOURCE"}


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="Master OAth", description="Credential-free multi-route authentication & DNS readback")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("route")
    p.add_argument("--provider", choices=sorted(ALLOWED_PROVIDER), required=True)
    p.add_argument("--operation", required=True)
    p.add_argument("--domain", default="")
    p.add_argument("--connected", action="store_true")
    d = sub.add_parser("dns")
    d.add_argument("--domain", required=True)
    v = sub.add_parser("summarize-dns")
    v.add_argument("--domain", required=True)
    b = sub.add_parser("browser-handoff")
    b.add_argument("--provider", choices=["chatgpt","hostinger","custom"], default="chatgpt")
    b.add_argument("--url", default="")
    b.add_argument("--open", action="store_true", help="open site in current device browser; no login claims")
    sub.add_parser("status")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "route":
            print_json(route(args.provider, args.operation, connected=args.connected, domain=args.domain))
        elif args.cmd == "dns":
            token = os.environ.get("MASTER_OATH_HOSTINGER_BEARER", "")
            if not token:
                print_json(route("hostinger", "dns_records_list", connected=False, domain=args.domain))
                return 2
            print_json(RemoteMCP(token).dns(args.domain))
        elif args.cmd == "summarize-dns":
            print_json(summarize_dns(sys.stdin.read(), args.domain))
        elif args.cmd == "browser-handoff":
            print_json(browser_handoff(args.provider, open_browser=args.open, url=args.url))
        else:
            print_json({"hostinger_mcp_url": HOSTINGER_MCP_URL, "bearer_available_in_process":
                        bool(os.environ.get("MASTER_OATH_HOSTINGER_BEARER")),
                        "gmail": "USE_CONNECTED_GMAIL_PLUGIN_NOT_A_PASSWORD", "secrets_written": False})
        return 0
    except AuthRouteError as exc:
        print_json({"error": str(exc), "done": False})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
