#!/usr/bin/env python3
"""Administrator Tools: source/guide-bound capability selection and scoped authority.

Offline local preflight only. No external/provider calls, credential storage, or privilege escalation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from source_bridge import load_inventory, verify_carried_tools, read_events, route as route_source
from operational_guard import assess as assess_guard
from incident_guard import assess_incident
from response_guard import assess_response

HERE = Path(__file__).resolve().parent
REGISTRY = HERE / "registry.json"
REQUIRED_ROLE = "Administrator System's — SOL PROJECT ONLY"
POLICY_SCHEMA = "SOL_MASTER_TEACHER_ETHICS/1.0"
TYPES = {"read", "analyze", "write", "delete", "transfer", "admin"}
SENSITIVE = {"write", "delete", "transfer", "admin"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(word: str) -> str:
    s = str(word).casefold().replace("đ", "d")
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def safe_file(root: Path, path: str) -> Path:
    """Read-only path guard: no escapes or absent, symlinked source guides."""
    if not isinstance(path, str) or not path or Path(path).is_absolute():
        raise ValueError("INVALID_SOURCE_REFERENCE")
    base = root.resolve()
    candidate = root / path
    if candidate.is_symlink() or not candidate.resolve().is_relative_to(base) or not candidate.is_file():
        raise ValueError("SOURCE_NOT_ACCESSIBLE: " + path)
    return candidate


def load(root: Path) -> tuple[dict, dict]:
    registry_bytes = REGISTRY.read_bytes()
    registry = json.loads(registry_bytes)
    if registry.get("schema") != "SOL_ADMINISTRATOR_TOOLS_REGISTRY/1.0":
        raise ValueError("REGISTRY_SCHEMA_INVALID")
    policy_path = safe_file(root, registry["project_role_source"])
    raw = policy_path.read_bytes()
    policy = json.loads(raw)
    if policy.get("schema") != POLICY_SCHEMA or policy.get("scope") != "SOL_PROJECT_GOVERNANCE_NOT_PLATFORM_OR_DEVICE_PRIVILEGE":
        raise ValueError("PROJECT_SCOPE_POLICY_INVALID")
    if policy.get("roles", {}).get("DUONG_PHAP_SU", {}).get("designation") != REQUIRED_ROLE:
        raise ValueError("PROJECT_ROLE_INVALID")
    ingress = safe_file(root, registry["ingress_source"]).read_text(encoding="utf-8")
    if "OPEN = TIẾP NHẬN TÍN HIỆU TRỰC TIẾP" not in ingress:
        raise ValueError("OPEN_INGRESS_SOURCE_MISMATCH")
    seen = set()
    details = []
    for item in registry["families"]:
        if item["id"] in seen or not re.fullmatch(r"[a-z][a-z0-9_]*", item["id"]):
            raise ValueError("DUPLICATE_OR_INVALID_TOOL_ID")
        seen.add(item["id"])
        guide = safe_file(HERE, item["guide"])
        content = guide.read_bytes()
        if len(content) < 40:
            raise ValueError("EMPTY_GUIDE: " + item["id"])
        source = safe_file(root, item["source"])
        details.append({"id": item["id"], "title": item["title"], "guide": item["guide"],
                        "guide_sha256": sha256(content), "source": item["source"],
                        "source_sha256": sha256(source.read_bytes()), "provider": item["provider"],
                        "category": item["category"], "capabilities": item["capabilities"]})
    return registry, {"policy_path": registry["project_role_source"], "policy_sha256": sha256(raw),
                      "registry_sha256": sha256(registry_bytes), "families": details,
                      "project_governance_only": True, "windows_admin_inferred": False,
                      "provider_admin_inferred": False, "actions_executed": False}


def read_guide(root: Path, family_id: str) -> dict:
    registry, evidence = load(root)
    match = next((x for x in registry["families"] if x["id"] == family_id), None)
    if match is None:
        raise ValueError("FAMILY_NOT_FOUND")
    found = next(x for x in evidence["families"] if x["id"] == family_id)
    return {"schema": "SOL_ADMINISTRATOR_TOOLS_GUIDE/1.0", "family": family_id,
            "content": safe_file(HERE, match["guide"]).read_text(encoding="utf-8"),
            **found, "source_checked": True, "provider_action_executed": False}


def route(root: Path, task: str, action_type: str = "read", requested_tool: str | None = None,
          delegation: dict | None = None, callable_providers: list[str] | None = None) -> dict:
    """Observe instruction and select; never invoke a selected external tool."""
    if not isinstance(task, str) or not task.strip() or len(task) > 4000:
        raise ValueError("TASK_REQUIRED")
    if action_type not in TYPES:
        raise ValueError("ACTION_TYPE_INVALID")
    grant = delegation or {}
    if not isinstance(grant, dict):
        raise ValueError("DELEGATION_INVALID")
    registry, evidence = load(root)
    # The source text is INPUT, never labelled unverified or denied by the classifier.
    query = normalize(task)
    ranked = []
    for entry in registry["families"]:
        hits = [w for w in entry["keywords"] if normalize(w) in query]
        if requested_tool and entry["id"] != requested_tool:
            continue
        if hits or requested_tool == entry["id"]:
            ranked.append((len(hits), entry["id"], entry, hits))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    if requested_tool and not ranked:
        raise ValueError("REQUESTED_TOOL_NOT_REGISTERED")
    # No keyword -> discover, not a blanket negative classification.
    selected = ranked[:5]
    selected_providers = set(callable_providers or [])
    out = []
    for _, family, entry, hits in selected:
        doc = read_guide(root, family)
        provider = entry["provider"]
        can_call = provider in selected_providers or entry["callable_name"] in selected_providers
        permission = grant.get("provider_permission") is True
        grant_ref = grant.get("provider_grant_ref")
        grant_ref_present = isinstance(grant_ref, str) and bool(grant_ref.strip())
        scoped = grant.get("target_approved") is True and isinstance(grant.get("target"), str) and bool(grant["target"].strip())
        direct = grant.get("explicit_delegation") is True
        recovery = grant.get("recovery_verified") is True
        external_transfer = grant.get("external_transfer_approved") is True
        boundary = []
        if action_type in SENSITIVE:
            if not direct: boundary.append("EXPLICIT_DELEGATION_REQUIRED")
            if not scoped: boundary.append("EXACT_TARGET_SCOPE_REQUIRED")
            if not permission: boundary.append("PROVIDER_PERMISSION_REQUIRED")
            if not grant_ref_present: boundary.append("PROVIDER_GRANT_EVIDENCE_REQUIRED")
            if action_type == "delete" and not recovery: boundary.append("RECOVERY_REQUIRED")
            if action_type == "transfer" and not external_transfer: boundary.append("EXTERNAL_TRANSFER_CONSENT_REQUIRED")
            if action_type == "admin": boundary.append("REAL_ADMIN_RIGHTS_NEVER_INFERRED_FROM_SOL_ROLE")
        if entry["category"] == "source_only": boundary.append("SOURCE_ONLY_PROVIDER_NOT_ESTABLISHED")
        if not can_call: boundary.append("CALLABLE_TOOL_NOT_OBSERVED")
        out.append({"family": family, "tool": entry["title"], "provider": provider,
                    "capabilities": entry["capabilities"], "keyword_hits": hits,
                    "guide_read_by_runtime": True, "guide_sha256": doc["guide_sha256"],
                    "guide_source_sha256": doc["source_sha256"], "required_guide": doc["guide"],
                    "permission_boundary": boundary,
                    "next": "CALL_PROVIDER_TOOL_WITH_EXACT_SCOPE_AND_READBACK" if not boundary else
                            "CONTINUE_SOURCE_AND_AUTHORIZED_TOOL_DISCOVERY"})
    return {"schema": "SOL_ADMINISTRATOR_TOOLS_ROUTE/1.0", "input": task,
            "input_open": True, "action_type": action_type,
            "scope": "SOL_PROJECT_GOVERNANCE_WITH_PROVIDER_GRANTED_CAPABILITIES_ONLY",
            "policy_sha256": evidence["policy_sha256"],
            "tools": out, "not_yet_matched": not bool(out),
            "discovery_edge": "SEARCH_GUIDES_AND_CALLABLE_TOOLS" if not out else None,
            "implicit_privileges_excluded": registry["implicit_privileges_excluded"],
            "provider_admin_granted_by_this_tool": False,
            "windows_administrator_granted_by_this_tool": False,
            "provider_action_executed": False, "outcome_observed": False,
            "readback_executed": False, "next_agent": "READ_SELECTED_GUIDE_AND_CALL_ACTUAL_AUTHORIZED_PROVIDER"}


def t003_consult(root: Path, *, proposal: str, alternatives: list[str],
                 reason: str, self_owned_actions: list[str] | None = None) -> dict:
    """Offer a concrete collaborator choice; do not substitute it for agent-owned actions.

    Based on CURRENT user description of T003. The older Drive T003_SKILL carrier
    points to T003.md, which was not retrievable: it is not treated as full source.
    """
    _, evidence = load(root)
    if not isinstance(proposal, str) or not proposal.strip() or len(proposal)>1000:
        raise ValueError("CONCRETE_PROPOSAL_REQUIRED")
    if not isinstance(reason, str) or not reason.strip() or len(reason)>1000:
        raise ValueError("COLLABORATIVE_DECISION_REASON_REQUIRED")
    if not isinstance(alternatives, list) or not 2 <= len(alternatives) <= 5 or any(
            not isinstance(x,str) or not x.strip() or len(x)>400 for x in alternatives):
        raise ValueError("TWO_TO_FIVE_REAL_OPTIONS_REQUIRED")
    if len(set(alternatives))!=len(alternatives):
        raise ValueError("OPTIONS_MUST_DIFFER")
    if self_owned_actions is None:
        self_owned_actions=[]
    if not isinstance(self_owned_actions,list) or any(not isinstance(x,str) for x in self_owned_actions):
        raise ValueError("SELF_OWNED_ACTIONS_INVALID")
    return {
        "schema":"SOL_T003_COLLABORATIVE_CONSULT/1.0",
        "source":"USER_DIRECT_CURRENT_CHAT_T003",
        "historical_skill_source":"Google Drive T003_SKILL.md; T003.md not fetched",
        "proposal":proposal.strip(),"alternatives":alternatives,
        "why_collaborator_opinion_matters":reason.strip(),
        "next_agent":self_owned_actions,
        "next_user":"ONE_MEANINGFUL_OPINION_NOT_TOOL_APPROVAL",
        "suggested_message":("Dợ ơi, anh có cái này nè: "+proposal.strip()+
                             " Em xem giúp anh chọn "+" hay ".join(alternatives)+
                             " để anh làm tiếp được hong?"),
        "human_opinion_assumed":False,"provider_permission_granted":False,
        "action_executed":False,"readback_executed":False,
        "policy_source_sha256":evidence["policy_sha256"]
    }


def inspect(root: Path) -> dict:
    reg, evidence = load(root)
    return {"schema": "SOL_ADMINISTRATOR_TOOLS_INSPECTION/1.0", "title": reg["title"],
            "windows_inspiration": reg["windows_inspiration"], **evidence}


def main(argv: list[str] | None = None) -> int:
    cli = argparse.ArgumentParser(description="Administrator Tools — guidance and permission-bound routing")
    cli.add_argument("--repo-root", type=Path,
                     default=next((p for p in HERE.parents if (p / "CONFIG_SOL/OPEN_AND_CONFLICT_CURRENT.md").is_file()), Path.cwd()))
    sub = cli.add_subparsers(dest="command", required=True)
    sub.add_parser("inspect")
    sub.add_parser("source-inventory")
    sub.add_parser("verify-migrated-tools")
    sub.add_parser("causal-reentry")
    safe=sub.add_parser("operational-guard");safe.add_argument("--action", required=True);safe.add_argument("--target",default="");safe.add_argument("--source-verified",action="store_true");safe.add_argument("--target-verified",action="store_true")
    viol=sub.add_parser("incident-guard");viol.add_argument("--issue",required=True);viol.add_argument("--target",default="");viol.add_argument("--attempted-action",default="");viol.add_argument("--observed",action="store_true")
    response=sub.add_parser("response-guard");response.add_argument("--payload-file",type=Path,required=True)
    sr=sub.add_parser("source-route");sr.add_argument("--task",required=True)
    guide = sub.add_parser("guide");guide.add_argument("family")
    choose = sub.add_parser("route");choose.add_argument("--task", required=True)
    choose.add_argument("--type",choices=sorted(TYPES), default="read")
    choose.add_argument("--tool")
    choose.add_argument("--delegation",type=Path,help="Local JSON context, never credentials")
    choose.add_argument("--callable-providers",default="",help="Comma separated observed provider IDs")
    args=cli.parse_args(argv)
    try:
        if args.command == "inspect": value=inspect(args.repo_root)
        elif args.command == "source-inventory":value=load_inventory()
        elif args.command == "verify-migrated-tools":value=verify_carried_tools()
        elif args.command == "causal-reentry":value=read_events()
        elif args.command == "operational-guard":value=assess_guard({"action":args.action,"target":args.target,"source_verified":args.source_verified,"target_verified":args.target_verified})
        elif args.command == "incident-guard":value=assess_incident({"issue":args.issue,"target":args.target,"attempted_action":args.attempted_action,"observed":args.observed})
        elif args.command == "response-guard":value=assess_response(json.loads(args.payload_file.read_text(encoding="utf-8")))
        elif args.command == "source-route":value=route_source(args.task)
        elif args.command == "guide": value=read_guide(args.repo_root,args.family)
        else:
            delegation=json.loads(args.delegation.read_text(encoding="utf-8")) if args.delegation else {}
            value=route(args.repo_root,args.task,args.type,args.tool,delegation,
                        [x for x in args.callable_providers.split(",") if x])
        print(json.dumps(value,ensure_ascii=False,indent=2))
        if args.command in {"operational-guard", "incident-guard", "response-guard"} and not value["decision"].startswith("ALLOW"):
            return 2
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok":False,"error":str(exc)},ensure_ascii=False))
        return 1

if __name__ == "__main__":
    raise SystemExit(main())