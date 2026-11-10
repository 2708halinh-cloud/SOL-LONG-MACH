#!/usr/bin/env python3
"""Minimal stdio MCP bridge for guide, inspect, route. No provider mutations."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from administrator_tools import inspect, read_guide, route, t003_consult
from source_bridge import load_inventory, verify_carried_tools, read_events, route as route_source
from operational_guard import assess as assess_guard
from incident_guard import assess_incident
from response_guard import assess_response

VERSION = "2024-11-05"
TOOLS = [
    {"name":"administrator_tools.incident_guard","description":"Detect repeated OPEN/tool-choice failures; fail closed with AGENT corrective action. NEVER deletes user folders or performs Windows operations.","inputSchema":{"type":"object","properties":{"issue":{"type":"string"},"target":{"type":"string"},"attempted_action":{"type":"string"},"observed":{"type":"boolean"},"task_open":{"type":"boolean"},"evidence":{"type":"array"}},"required":["issue"],"additionalProperties":False}},
    {"name":"administrator_tools.response_guard", "description":"Prepublication validation of agent/model role, unfinished executable NEXT, and evidence-based READBACK. Blocks invalid output, NEVER formats disks.", "inputSchema":{"type":"object","properties":{"mode":{"type":"string"},"output":{"type":"string"},"task_open":{"type":"boolean"},"pending_agent_actions":{"type":"array","items":{"type":"string"}},"completed_agent_actions":{"type":"array"},"provider_receipts":{"type":"array"},"user_instruction":{"type":"string"},"user_feedback_question":{"type":"string"},"agent_next_action":{"type":"string"},"claims_external_success":{"type":"boolean"}},"required":["output"],"additionalProperties":False}},
    {"name":"administrator_tools.operational_guard", "description":"Fail-closed STOP/READBACK/NEXT action preflight. Blocks volume formatting, fake completion, and unknown operations; returns next actor and action. No OS writes.", "inputSchema":{"type":"object","properties":{"action":{"type":"string"},"target":{"type":"string"},"source_verified":{"type":"boolean"},"target_verified":{"type":"boolean"},"receipts":{"type":"array","items":{"type":"object"}}},"required":["action"],"additionalProperties":False}},
    {"name":"administrator_tools.source_inventory","description":"Read canonical .codex and .docker source directory inventory.","inputSchema":{"type":"object","properties":{},"additionalProperties":False}},
    {"name":"administrator_tools.verify_migrated_tools","description":"Hash-verify imported .codex PowerShell source scripts.","inputSchema":{"type":"object","properties":{},"additionalProperties":False}},
    {"name":"administrator_tools.causal_reentry","description":"Restore user-supplied lost message and validate event hash chain before resuming unfinished tool migration.","inputSchema":{"type":"object","properties":{},"additionalProperties":False}},
    {"name":"administrator_tools.source_route","description":"Find source carrier for Docker/Codex task while preserving actual pending action.","inputSchema":{"type":"object","properties":{"task":{"type":"string"}},"required":["task"],"additionalProperties":False}},
    {"name":"administrator_tools.inspect", "description":"Read Administrator Tools registry, source evidence and capability guides. No external actions.",
     "inputSchema":{"type":"object","properties":{},"additionalProperties":False}},
    {"name":"administrator_tools.guide", "description":"Read one verified tool guide before selection or use.",
     "inputSchema":{"type":"object","properties":{"family":{"type":"string"}},"required":["family"],"additionalProperties":False}},
    {"name":"administrator_tools.consult_t003", "description":"Ask one meaningful companion opinion at an actual unresolved choice, and retain executable agent-owned actions.",
     "inputSchema":{"type":"object","properties":{"proposal":{"type":"string"},"alternatives":{"type":"array","items":{"type":"string"},"minItems":2,"maxItems":5},"reason":{"type":"string"},"self_owned_actions":{"type":"array","items":{"type":"string"}}},"required":["proposal","alternatives","reason"],"additionalProperties":False}},
    {"name":"administrator_tools.route", "description":"Find suitable guide, permission scope, callable provider and next edge; does not execute provider operation.",
     "inputSchema":{"type":"object","properties":{"task":{"type":"string"},"action_type":{"type":"string","enum":["read","analyze","write","delete","transfer","admin"]},"requested_tool":{"type":"string"},"delegation":{"type":"object"},"callable_providers":{"type":"array","items":{"type":"string"}}},"required":["task"],"additionalProperties":False}},
]

def handle(message: dict, root: Path) -> dict | None:
    ident = message.get("id")
    method = message.get("method")
    if method == "notifications/initialized": return None
    response={"jsonrpc":"2.0","id":ident}
    try:
        if method == "initialize":
            result={"protocolVersion":VERSION,"capabilities":{"tools":{}},"serverInfo":{"name":"Administrator Tools","version":"1.0.0"}}
        elif method == "ping": result={}
        elif method == "tools/list": result={"tools":TOOLS}
        elif method == "tools/call":
            params=message.get("params") or {}; args=params.get("arguments") or {}
            name=params.get("name")
            if name == "administrator_tools.operational_guard": data=assess_guard(args)
            elif name == "administrator_tools.incident_guard": data=assess_incident(args)
            elif name == "administrator_tools.response_guard": data=assess_response(args)
            elif name == "administrator_tools.source_inventory": data=load_inventory()
            elif name == "administrator_tools.verify_migrated_tools": data=verify_carried_tools()
            elif name == "administrator_tools.causal_reentry": data=read_events()
            elif name == "administrator_tools.source_route": data=route_source(args["task"])
            elif name == "administrator_tools.inspect": data=inspect(root)
            elif name == "administrator_tools.guide": data=read_guide(root,args["family"])
            elif name == "administrator_tools.consult_t003":
                data=t003_consult(root,proposal=args["proposal"],alternatives=args["alternatives"],reason=args["reason"],self_owned_actions=args.get("self_owned_actions"))
            elif name == "administrator_tools.route":
                data=route(root,args["task"],args.get("action_type","read"),args.get("requested_tool"),
                           args.get("delegation"),args.get("callable_providers"))
            else: raise ValueError("UNKNOWN_TOOL")
            result={"content":[{"type":"text","text":json.dumps(data,ensure_ascii=False)}],"isError":False}
        else: raise ValueError("UNKNOWN_METHOD")
        response["result"]=result
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        if method == "tools/call":
            response["result"]={"content":[{"type":"text","text":json.dumps({"error":str(exc)},ensure_ascii=False)}],"isError":True}
        else: response["error"]={"code":-32602,"message":str(exc)}
    return response

def serve(root: Path) -> None:
    for raw in sys.stdin:
        try:
            value=json.loads(raw)
            response=handle(value,root)
            if response is not None:
                sys.stdout.write(json.dumps(response,ensure_ascii=False)+"\n")
                sys.stdout.flush()
        except (ValueError,TypeError,json.JSONDecodeError) as exc:
            sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":None,"error":{"code":-32700,"message":str(exc)}})+"\n");sys.stdout.flush()

if __name__ == "__main__":
    import argparse
    cli=argparse.ArgumentParser()
    cli.add_argument("--repo-root",type=Path,required=True)
    opts=cli.parse_args()
    serve(opts.repo_root)