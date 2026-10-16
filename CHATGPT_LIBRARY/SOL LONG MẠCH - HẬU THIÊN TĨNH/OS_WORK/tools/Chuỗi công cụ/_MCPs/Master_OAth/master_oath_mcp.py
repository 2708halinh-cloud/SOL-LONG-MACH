#!/usr/bin/env python3
"""Stdio MCP adapter for Master OAth (no credentials persisted)."""
from __future__ import annotations
import json
import os
import sys
from master_oath import AuthRouteError, RemoteMCP, HOSTINGER_LOGIN, HOSTINGER_MCP_URL, route, summarize_dns, browser_handoff, CHATGPT_LOGIN

TOOLS = [
    {"name":"master_oath_route","description":"Route Hostinger DNS or Gmail reads via already-connected provider before OAuth fallback.",
     "inputSchema":{"type":"object","properties":{"provider":{"type":"string","enum":["hostinger","gmail"]},
        "operation":{"type":"string"},"domain":{"type":"string"},"connected":{"type":"boolean"}},
        "required":["provider","operation"]}},
    {"name":"master_oath_hostinger_dns","description":"Read a Hostinger DNS zone using process-local remote MCP Bearer; never reveal the token; redact DNS content.",
     "inputSchema":{"type":"object","properties":{"domain":{"type":"string"}},"required":["domain"]}},
    {"name":"master_oath_summarize_dns","description":"Convert provider zone JSON to redacted DNS name/type/TTL summary.",
     "inputSchema":{"type":"object","properties":{"domain":{"type":"string"},"zone":{"type":"array"}},
        "required":["domain","zone"]}},
    {"name":"master_oath_browser_handoff","description":"Prepare official ChatGPT, Hostinger or explicit HTTPS browser entry. Never captures password, cookies or claims login.",
     "inputSchema":{"type":"object","properties":{"provider":{"type":"string","enum":["chatgpt","hostinger","custom"]},"url":{"type":"string"},"open":{"type":"boolean"}}}},
    {"name":"master_oath_status","description":"Check configured remote transport without exposing secrets or attempting login.",
     "inputSchema":{"type":"object","properties":{}}}
]


def dispatch(method: str, params: dict) -> dict | None:
    if method == "initialize":
        return {"protocolVersion": "2025-03-26", "capabilities":{"tools":{"listChanged":False}},
                "serverInfo":{"name":"Master OAth", "version":"1.0.0"}}
    if method in ("ping",):
        return {}
    if method == "tools/list":
        return {"tools":TOOLS}
    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        if not isinstance(args,dict):
            raise AuthRouteError("INVALID_TOOL_ARGUMENTS")
        if name == "master_oath_route":
            value = route(args.get("provider", ""), args.get("operation", ""),
                          connected=bool(args.get("connected", False)), domain=args.get("domain", ""))
        elif name == "master_oath_hostinger_dns":
            token = os.environ.get("MASTER_OATH_HOSTINGER_BEARER", "")
            if not token:
                raise AuthRouteError("REMOTE_MCP_BEARER_NOT_CONFIGURED_USE_CONNECTED_HOSTINGER_PLUGIN")
            value = RemoteMCP(token).dns(args.get("domain", ""))
        elif name == "master_oath_summarize_dns":
            value = summarize_dns(args.get("zone"), args.get("domain", ""))
        elif name == "master_oath_browser_handoff":
            value = browser_handoff(args.get("provider", "chatgpt"),open_browser=bool(args.get("open",False)),url=args.get("url",""))
        elif name == "master_oath_status":
            value = {"hostinger_remote_url":HOSTINGER_MCP_URL,
                     "remote_token_present":bool(os.environ.get("MASTER_OATH_HOSTINGER_BEARER")),
                     "connected_chat_plugins":"USE_EXISTING_HOSTINGER_AND_GMAIL_TOOL_ROUTES",
                     "login_fallback":HOSTINGER_LOGIN,"chatgpt_browser_entry":CHATGPT_LOGIN,"credential_persistence":False}
        else:
            raise AuthRouteError("UNKNOWN_TOOL")
        return {"content":[{"type":"text","text":json.dumps(value,ensure_ascii=False,sort_keys=True)}],"isError":False}
    raise AuthRouteError("METHOD_NOT_SUPPORTED")


def run() -> None:
    for line in sys.stdin:
        try:
            msg = json.loads(line)
            if not isinstance(msg,dict):
                continue
            if msg.get("method"," ").startswith("notifications/") or "id" not in msg:
                continue
            try:
                result = dispatch(msg.get("method",""),msg.get("params") or {})
                response = {"jsonrpc":"2.0","id":msg["id"],"result":result}
            except (AuthRouteError,ValueError,TypeError,KeyError) as exc:
                # Never echo provider response, credentials or request bodies.
                response = {"jsonrpc":"2.0","id":msg["id"],
                            "error":{"code":-32001,"message":"Master OAth: "+str(exc)}}
            print(json.dumps(response,ensure_ascii=False),flush=True)
        except (json.JSONDecodeError,TypeError):
            continue

if __name__ == "__main__":
    run()
