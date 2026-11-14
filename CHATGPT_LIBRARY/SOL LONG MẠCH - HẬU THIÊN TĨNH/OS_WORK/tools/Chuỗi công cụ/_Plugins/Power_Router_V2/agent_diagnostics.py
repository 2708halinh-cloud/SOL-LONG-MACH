#!/usr/bin/env python3
"""SOL Agent Core diagnostics: offline, source-bound, read-only by default.

This module NEVER invokes arbitrary tools, uploads traces, edits sources,
discloses environment values, or claims a repair happened without readback.
Tool execution remains with the existing authorized POWER router / connectors.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
from decimal import Decimal, InvalidOperation
from pathlib import Path

VERSION = "SOL_AGENT_DIAGNOSTICS/1.0"
ENV_NAME = re.compile(r"^[A-Z][A-Z0-9_]{1,79}$")
INJECTION = re.compile(
    r"(ignore (all |your )?(previous|prior|system) instructions|"
    r"disregard (the )?(system|developer) (message|instructions)|"
    r"bypass (the )?(approval|guardrail|security)|"
    r"quên (mọi |tất cả )?(hướng dẫn|quy tắc) (trước|cũ))",
    re.IGNORECASE,
)
REPAIR_HINTS = {
    "CONTEXT_LOOP": "STOP_REPEATED_STEP_AND_SPLIT_ATOMIC_TASK",
    "TOOL_SCHEMA_INVALID": "REFETCH_REAL_TOOL_SCHEMA_AND_REBIND_ARGUMENTS",
    "PARAMETER_VALIDATION_FAILED": "REJECT_INVALID_TYPES_FORMATS_AND_REVALIDATE_TRUSTED_SCHEMA",
    "UNKNOWN_TOOL": "DISCOVER_CONNECTED_CAPABILITY_AND_CONFIRM_TOOL_ID",
    "GOAL_DRIFT": "RESTORE_ORIGINAL_GOAL_AND_CHECKPOINT",
    "UNTRUSTED_INSTRUCTION_SIGNAL": "ISOLATE_UNTRUSTED_SOURCE_AS_DATA",
    "TIMEOUT_EXCEEDED": "ABORT_CURRENT_ATTEMPT_AND_REPORT_TIMEOUT",
    "RETRY_BUDGET_EXCEEDED": "STOP_RETRIES_AND_INSPECT_PROVIDER_ERROR",
    "NON_IDEMPOTENT_RETRY": "STOP_RETRY_AND_CHECK_PRIOR_RECEIPT",
    "APPROVAL_REQUIRED": "WAIT_FOR_VERIFIABLE_HUMAN_APPROVAL",
    "ROLE_NOT_ALLOWED": "DENY_AND_REVALIDATE_CALLER_ROLE",
    "CONFIG_INVALID": "FIX_CONFIG_WITHOUT_EXPOSING_SECRETS",
    "ENV_MISSING": "PROVISION_SECRET_IN_AUTHORIZED_RUNTIME_NOT_SOURCE",
    "RECEIPT_UNVERIFIED": "READBACK_EXACT_TARGET_BEFORE_DONE",
    "TOKEN_BUDGET_EXCEEDED": "STOP_AND_REPLAN_SMALLER_TASK",
    "CHECKPOINT_GAP": "READ_LAST_DURABLE_CHECKPOINT",
    "UNSUPPORTED_COMPROMISE_INFERENCE": "RETRACT_UNVERIFIED_COMPROMISE_CLAIM_AND_REUSE_KNOWN_SECRET_POLICY",
    "REPEATED_SECURITY_LECTURE": "STOP_RETEACHING_ESTABLISHED_POLICY_AND_RETURN_TO_USER_GOAL",
}

def _issue(code: str, **fields) -> dict:
    return {"code": code, "next": REPAIR_HINTS[code], **fields}

def checked_config(tool: dict) -> tuple[dict, list[str]]:
    """Validate config, never output token values."""
    issues = []
    if not isinstance(tool, dict):
        tool = {}
        issues.append("TOOL_CONFIG_NOT_OBJECT")
    runtime = tool.get("runtime_config", {})
    policy = tool.get("security_policy", {})
    if not isinstance(runtime, dict) or not isinstance(policy, dict):
        issues.append("RUNTIME_OR_POLICY_NOT_OBJECT")
        runtime = runtime if isinstance(runtime, dict) else {}
        policy = policy if isinstance(policy, dict) else {}
    timeout = runtime.get("timeout", 30000)
    retries = runtime.get("max_retries", 0)
    if type(timeout) is not int or not 100 <= timeout <= 300000:
        issues.append("TIMEOUT_OUT_OF_RANGE")
        timeout = 30000
    if type(retries) is not int or not 0 <= retries <= 5:
        issues.append("RETRIES_OUT_OF_RANGE")
        retries = 0
    names = runtime.get("env_required", [])
    if not isinstance(names, list) or not all(
        isinstance(n, str) and ENV_NAME.fullmatch(n) for n in names
    ):
        issues.append("ENV_NAMES_INVALID")
        names = []
    roles = policy.get("allowed_roles", [])
    if not isinstance(roles, list) or not all(isinstance(r, str) and r for r in roles):
        issues.append("ROLES_INVALID")
        roles = []
    requires_approval = policy.get("requires_approval", False)
    if type(requires_approval) is not bool:
        issues.append("APPROVAL_FLAG_NOT_BOOLEAN")
        requires_approval = True  # conservative
    return {
        "timeout": timeout, "max_retries": retries,
        "env_required": names, "allowed_roles": roles,
        "requires_approval": requires_approval,
    }, issues

def _signature(step: dict) -> str:
    """Hash only structure; do not expose raw prompts/arguments in logs."""
    payload = {"tool": step.get("tool"), "arguments": step.get("arguments")}
    data = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def diagnose_run(run: dict) -> dict:
    if not isinstance(run, dict):
        raise ValueError("RUN_MUST_BE_JSON_OBJECT")
    findings = []
    config, faults = checked_config(run.get("tool_config", {}))
    if faults:
        findings.append(_issue("CONFIG_INVALID", faults=faults))
    if run.get("goal_id") and run.get("current_goal_id") and (
        run["goal_id"] != run["current_goal_id"]
    ) and run.get("goal_change_authorized") is not True:
        findings.append(_issue("GOAL_DRIFT"))
    steps = run.get("steps", [])
    if not isinstance(steps, list):
        findings.append(_issue("CONFIG_INVALID", faults=["STEPS_NOT_ARRAY"]))
        steps = []
    good_steps = [s for s in steps if isinstance(s, dict)]
    if len(good_steps) >= 3 and len({_signature(s) for s in good_steps[-3:]}) == 1:
        findings.append(_issue("CONTEXT_LOOP", repeated_steps=3))
    declared = run.get("tool_schemas", {})
    if not isinstance(declared, dict):
        declared = {}
        findings.append(_issue("CONFIG_INVALID", faults=["TOOL_SCHEMAS_NOT_OBJECT"]))
    call = run.get("tool_call")
    if call is not None:
        if not isinstance(call, dict):
            findings.append(_issue("TOOL_SCHEMA_INVALID"))
        elif call.get("name") not in declared:
            findings.append(_issue("UNKNOWN_TOOL"))
        else:
            spec = declared[call["name"]]
            args = call.get("arguments")
            if not isinstance(spec, dict) or not isinstance(args, dict):
                findings.append(_issue("TOOL_SCHEMA_INVALID"))
            else:
                fields = spec.get("parameters", [])
                required = spec.get("required", [])
                if (not isinstance(fields, list) or
                    not isinstance(required, list) or
                    any(not isinstance(v, str) for v in fields + required) or
                    set(args) - set(fields) or set(required) - set(args)):
                    findings.append(_issue("TOOL_SCHEMA_INVALID"))
                else:
                    rules = spec.get("parameter_rules", {})
                    invalid = []
                    if not isinstance(rules, dict):
                        invalid.append("parameter_rules")
                    else:
                        for name, rule in rules.items():
                            if name not in args:
                                continue
                            if not isinstance(rule, dict):
                                invalid.append(name)
                                continue
                            value = args[name]
                            expected = rule.get("type")
                            types = {
                                "string": lambda v: isinstance(v, str),
                                "integer": lambda v: type(v) is int,
                                "number": lambda v: type(v) in (int, float),
                                "boolean": lambda v: type(v) is bool,
                                "array": lambda v: isinstance(v, list),
                                "object": lambda v: isinstance(v, dict),
                            }
                            if expected is not None and (
                                expected not in types or not types[expected](value)
                            ):
                                invalid.append(name)
                                continue
                            if isinstance(value, str):
                                limit = rule.get("max_length", 10000)
                                if type(limit) is not int or not 1 <= limit <= 10000 or len(value) > limit:
                                    invalid.append(name)
                                if rule.get("format") == "identifier" and not re.fullmatch(
                                    r"[A-Za-z_][A-Za-z0-9_]{0,63}", value
                                ):
                                    invalid.append(name)
                                elif rule.get("format") not in (None, "identifier"):
                                    invalid.append(name)
                            if "enum" in rule and (
                                not isinstance(rule["enum"], list) or value not in rule["enum"]
                            ):
                                invalid.append(name)
                    if invalid:
                        findings.append(_issue("PARAMETER_VALIDATION_FAILED",
                                               invalid_parameter_names=sorted(set(invalid))))
    text = run.get("untrusted_text", "")
    if isinstance(text, str) and INJECTION.search(text[:20000]):
        findings.append(_issue("UNTRUSTED_INSTRUCTION_SIGNAL", certainty="SUSPECTED_NOT_PROVEN"))
    elapsed = run.get("elapsed_ms", 0)
    if type(elapsed) in (int, float) and elapsed > config["timeout"]:
        findings.append(_issue("TIMEOUT_EXCEEDED"))
    attempts = run.get("attempts", 1)
    if type(attempts) is int and attempts > config["max_retries"] + 1:
        findings.append(_issue("RETRY_BUDGET_EXCEEDED"))
    if type(attempts) is int and attempts > 1 and run.get("idempotent") is not True:
        findings.append(_issue("NON_IDEMPOTENT_RETRY"))
    policy = config
    if run.get("requested_execution") is True:
        if policy["requires_approval"] and run.get("approval_receipt_verified") is not True:
            findings.append(_issue("APPROVAL_REQUIRED"))
        if policy["allowed_roles"] and run.get("actor_role") not in policy["allowed_roles"]:
            findings.append(_issue("ROLE_NOT_ALLOWED"))
        missing = [n for n in policy["env_required"] if n not in os.environ]
        if missing:
            findings.append(_issue("ENV_MISSING", required_variable_names=missing))
        if run.get("execution_receipt_verified") is not True and run.get("action_executed") is True:
            findings.append(_issue("RECEIPT_UNVERIFIED"))
    used, budget = run.get("tokens_used"), run.get("token_budget")
    if (type(used) is int and type(budget) is int and budget >= 0 and used > budget):
        findings.append(_issue("TOKEN_BUDGET_EXCEEDED"))
    if run.get("checkpoint_expected") is True and run.get("checkpoint_found") is False:
        findings.append(_issue("CHECKPOINT_GAP"))
    # Inspect declarative flags only: never handle credential/token values.
    response = run.get("credential_response")
    if response is not None:
        allowed = {"authorized_handoff", "existing_policy_known", "exposure_verified",
                   "assistant_asserted_compromise", "assistant_repeated_policy_lecture"}
        if not isinstance(response, dict) or set(response) - allowed or any(
            type(value) is not bool for value in response.values()
        ):
            findings.append(_issue("CONFIG_INVALID", faults=["CREDENTIAL_RESPONSE_METADATA_INVALID"]))
        else:
            if (response.get("assistant_asserted_compromise") is True
                and response.get("exposure_verified") is not True):
                findings.append(_issue("UNSUPPORTED_COMPROMISE_INFERENCE"))
            if (response.get("authorized_handoff") is True
                and response.get("existing_policy_known") is True
                and response.get("assistant_repeated_policy_lecture") is True):
                findings.append(_issue("REPEATED_SECURITY_LECTURE"))
    status = "NEEDS_REPAIR" if findings else "NO_DETERMINISTIC_FAULT_FOUND"
    return {
        "schema": VERSION, "status": status,
        "source": "LOCAL_DETERMINISTIC_DIAGNOSTIC",
        "findings": findings,
        "repair_plan": [f["next"] for f in findings],
        "action_executed": False, "provider_called": False,
        "approval_state": "NOT_GRANTED_BY_DIAGNOSIS",
        "readback_state": "NOT_APPLICABLE_NO_MUTATION",
        "dry_run": True,
        "observability": {"local_summary": True, "langfuse_connected": False,
                          "langsmith_connected": False, "raw_prompts_exported": False},
    }

def arithmetic(expression: str) -> str:
    """Decimal arithmetic without eval(), network access or third-party calculator."""
    if not isinstance(expression, str) or len(expression) > 160:
        raise ValueError("EXPRESSION_LENGTH_INVALID")
    tree = ast.parse(expression, mode="eval")
    def visit(node, depth=0):
        if depth > 16:
            raise ValueError("EXPRESSION_TOO_DEEP")
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return Decimal(str(node.value))
        if isinstance(node, ast.UnaryOp) and type(node.op) in (ast.UAdd, ast.USub):
            v = visit(node.operand, depth+1)
            return v if isinstance(node.op, ast.UAdd) else -v
        if isinstance(node, ast.BinOp) and type(node.op) in (
            ast.Add, ast.Sub, ast.Mult, ast.Div
        ):
            a, b = visit(node.left, depth+1), visit(node.right, depth+1)
            if isinstance(node.op, ast.Add):
                return a+b
            if isinstance(node.op, ast.Sub):
                return a-b
            if isinstance(node.op, ast.Mult):
                return a*b
            if b == 0:
                raise ValueError("DIVISION_BY_ZERO")
            return a/b
        raise ValueError("EXPRESSION_OPERATOR_DENIED")
    try:
        result = visit(tree.body)
    except (InvalidOperation, OverflowError) as exc:
        raise ValueError("ARITHMETIC_INVALID") from exc
    if not result.is_finite() or abs(result) > Decimal("1e100"):
        raise ValueError("ARITHMETIC_BOUND_EXCEEDED")
    return format(result.normalize(), "f")

def storage_inventory(root: Path, max_files: int = 5000) -> dict:
    """Read-only bounded storage summary. Never follows symlinks or lists names."""
    root = Path(root).resolve(strict=True)
    if not root.is_dir() or max_files < 1 or max_files > 50000:
        raise ValueError("STORAGE_SCOPE_INVALID")
    count, total, skipped = 0, 0, 0
    pending = [root]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_symlink():
                    skipped += 1
                    continue
                if entry.is_dir(follow_symlinks=False):
                    pending.append(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    count += 1
                    total += entry.stat(follow_symlinks=False).st_size
                    if count >= max_files:
                        return {"files": count, "bytes": total,
                                "symlinks_skipped": skipped, "truncated": True,
                                "read_only": True}
    return {"files": count, "bytes": total,
            "symlinks_skipped": skipped, "truncated": False, "read_only": True}

def enforce_redmi_runtime() -> None:
    """SOL source execution policy: fail closed outside authorized Redmi Termux."""
    if os.environ.get("PREFIX") != "/data/data/com.termux/files/usr":
        raise RuntimeError("REDMI_TERMUX_REQUIRED")
    getprop = Path("/system/bin/getprop")
    if not getprop.is_file():
        raise RuntimeError("REDMI_GETPROP_REQUIRED")
    models = []
    for field in ("ro.product.marketname", "ro.product.model"):
        reply = subprocess.run([str(getprop), field], timeout=3,
                               text=True, capture_output=True, check=False)
        if reply.returncode == 0:
            models.append(reply.stdout.casefold())
    if not any("redmi note 14 pro" in model for model in models):
        raise RuntimeError("REDMI_IDENTITY_NOT_VERIFIED")
    if not Path.cwd().resolve().is_relative_to(Path("/storage/emulated/0").resolve()):
        raise RuntimeError("SHARED_STORAGE_CWD_REQUIRED")

def main():
    p = argparse.ArgumentParser(description="SOL read-only Agent diagnostic")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--diagnose", type=Path)
    group.add_argument("--arithmetic")
    group.add_argument("--storage", type=Path)
    args = p.parse_args()
    enforce_redmi_runtime()
    shared = Path("/storage/emulated/0").resolve()
    target = args.diagnose if args.diagnose is not None else args.storage
    if target is not None and not target.resolve().is_relative_to(shared):
        raise ValueError("TARGET_OUTSIDE_AUTHORIZED_SHARED_STORAGE")
    if args.diagnose:
        if args.diagnose.stat().st_size > 100_000:
            raise ValueError("INPUT_OVERSIZE")
        result = diagnose_run(json.loads(args.diagnose.read_text(encoding="utf-8")))
    elif args.arithmetic is not None:
        result = {"arithmetic": arithmetic(args.arithmetic), "provider_called": False}
    else:
        result = storage_inventory(args.storage)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
