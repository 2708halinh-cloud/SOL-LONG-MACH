"""Conservative outbound network policy evaluation.

This module only evaluates a local policy and, for the explicit connect tool,
opens a short-lived TCP connection after the policy allows the destination. It
does not act as a browser proxy or claim to control unrelated cloud traffic.
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
from pathlib import Path
import socket
from typing import Any


class NetworkPolicyError(ValueError):
    """The policy or destination is invalid."""


def _dns(value: Any, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise NetworkPolicyError(f"{field} must contain non-empty strings")
    value = value.strip().lower().rstrip(".")
    if not value or any(ch.isspace() for ch in value) or "/" in value or ":" in value:
        raise NetworkPolicyError(f"invalid DNS pattern in {field}")
    if value.startswith("*."):
        if value.count("*") != 1 or value[2:].count(".") < 1:
            raise NetworkPolicyError(f"invalid wildcard DNS pattern in {field}")
    elif "*" in value or value.count(".") < 1:
        raise NetworkPolicyError(f"invalid DNS name in {field}")
    return value


def _cidrs(values: Any, *, field: str) -> list[ipaddress._BaseNetwork]:
    if values is None:
        values = []
    if not isinstance(values, list):
        raise NetworkPolicyError(f"{field} must be an array")
    result: list[ipaddress._BaseNetwork] = []
    for value in values:
        if not isinstance(value, str):
            raise NetworkPolicyError(f"{field} must contain strings")
        try:
            result.append(ipaddress.ip_network(value.strip(), strict=False))
        except ValueError as exc:
            raise NetworkPolicyError(f"invalid CIDR in {field}: {value}") from exc
    return result


def _names(values: Any, *, field: str) -> list[str]:
    if values is None:
        values = []
    if not isinstance(values, list):
        raise NetworkPolicyError(f"{field} must be an array")
    return [_dns(value, field=field) for value in values]


def _section(raw: Any, *, field: str) -> dict[str, Any]:
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise NetworkPolicyError(f"{field} must be an object")
    return {
        "ip_cidrs": _cidrs(raw.get("ip_cidrs", []), field=f"{field}.ip_cidrs"),
        "dns": _names(raw.get("dns", []), field=f"{field}.dns"),
    }


def load_policy(path: Path | None) -> dict[str, Any]:
    """Load and validate policy. Missing path means deny-by-default baseline."""
    if path is None:
        return {
            "configured": False,
            "path": None,
            "sha256": None,
            "version": 1,
            "default_action": "deny",
            "always_allow": _section({}, field="always_allow"),
            "block": _section({}, field="block"),
            "source": "built_in_deny_by_default",
        }
    try:
        raw_bytes = path.read_bytes()
        raw = json.loads(raw_bytes.decode("utf-8"))
    except FileNotFoundError as exc:
        raise NetworkPolicyError("network policy file not found") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise NetworkPolicyError("network policy file is not valid UTF-8 JSON") from exc
    if not isinstance(raw, dict):
        raise NetworkPolicyError("network policy root must be an object")
    if raw.get("version", 1) != 1:
        raise NetworkPolicyError("unsupported network policy version")
    default_action = raw.get("default_action", "deny")
    if default_action != "deny":
        raise NetworkPolicyError("default_action must be deny")
    return {
        "configured": True,
        "path": str(path),
        "sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "version": 1,
        "default_action": "deny",
        "always_allow": _section(raw.get("always_allow"), field="always_allow"),
        "block": _section(raw.get("block"), field="block"),
        "source": raw.get("source", "local_policy_file"),
    }


def _ip(value: str) -> ipaddress._BaseAddress | None:
    try:
        return ipaddress.ip_address(value.strip("[]"))
    except ValueError:
        return None


def canonical_host(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise NetworkPolicyError("host is required")
    host = value.strip().lower().rstrip(".")
    if any(ch.isspace() for ch in host) or "/" in host:
        raise NetworkPolicyError("host must be a DNS name or IP address, without a URL or path")
    if _ip(host) is None and ("*" in host or ":" in host):
        raise NetworkPolicyError("invalid host")
    return host


def _dns_match(host: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        if pattern.startswith("*."):
            suffix = pattern[1:]
            if host.endswith(suffix) and host != pattern[2:]:
                return pattern
        elif host == pattern:
            return pattern
    return None


def _cidr_match(address: ipaddress._BaseAddress, networks: list[ipaddress._BaseNetwork]) -> str | None:
    for network in networks:
        if address in network:
            return str(network)
    return None


def resolve_host(host: str) -> list[str]:
    """Resolve without opening an application connection; return unique IPs."""
    address = _ip(host)
    if address is not None:
        return [str(address)]
    try:
        records = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise NetworkPolicyError(f"DNS resolution failed: {host}") from exc
    result: list[str] = []
    for record in records:
        candidate = record[4][0]
        if candidate not in result:
            result.append(candidate)
    if not result:
        raise NetworkPolicyError(f"DNS returned no address: {host}")
    return result


def evaluate(host: str, policy: dict[str, Any], *, resolve_dns: bool = True) -> dict[str, Any]:
    """Return an auditable decision; block rules always win over allow rules."""
    host = canonical_host(host)
    address = _ip(host)
    allow_dns = None if address is not None else _dns_match(host, policy["always_allow"]["dns"])
    block_dns = None if address is not None else _dns_match(host, policy["block"]["dns"])
    addresses: list[str] = []
    if address is not None:
        addresses = [str(address)]
    # A matching DNS block is sufficient evidence to deny; do not query an
    # explicitly blocked name. Allowed names are resolved so returned IPs can
    # still be checked against the IP blocklist.
    elif resolve_dns and allow_dns is not None and block_dns is None:
        addresses = resolve_host(host)

    blocked: list[dict[str, str]] = []
    allowed: list[dict[str, str]] = []
    if block_dns is not None:
        blocked.append({"kind": "dns", "rule": block_dns})
    if allow_dns is not None:
        allowed.append({"kind": "dns", "rule": allow_dns})
    for value in addresses:
        ip_value = _ip(value)
        if ip_value is None:
            continue
        block_rule = _cidr_match(ip_value, policy["block"]["ip_cidrs"])
        allow_rule = _cidr_match(ip_value, policy["always_allow"]["ip_cidrs"])
        if block_rule:
            blocked.append({"kind": "ip", "rule": block_rule, "address": value})
        if allow_rule:
            allowed.append({"kind": "ip", "rule": allow_rule, "address": value})

    if blocked:
        decision = "blocked"
        reason = "block_rule" if not allowed else "block_precedence_conflict"
    elif allowed:
        decision = "allowed"
        reason = "always_allow_rule"
    else:
        decision = "blocked"
        reason = "default_deny"
    return {
        "decision": decision,
        "host": host,
        "resolved_addresses": addresses,
        "matched_allow": allowed,
        "matched_block": blocked,
        "reason": reason,
        "default_action": policy["default_action"],
    }


def summary(policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "configured": policy["configured"],
        "path": policy["path"],
        "sha256": policy["sha256"],
        "version": policy["version"],
        "default_action": policy["default_action"],
        "source": policy["source"],
        "always_allow": {
            "ip_cidrs": [str(x) for x in policy["always_allow"]["ip_cidrs"]],
            "dns": policy["always_allow"]["dns"],
        },
        "block": {
            "ip_cidrs": [str(x) for x in policy["block"]["ip_cidrs"]],
            "dns": policy["block"]["dns"],
        },
        "enforcement_scope": "explicit MCP network tools only; not cloud-browser traffic",
    }


def connect(host: str, port: int, timeout: int, policy: dict[str, Any]) -> dict[str, Any]:
    """Open and immediately close TCP connections to policy-approved addresses."""
    decision = evaluate(host, policy, resolve_dns=True)
    if decision["decision"] != "allowed":
        raise PermissionError(f"network destination blocked: {decision['reason']}")
    attempts = []
    for address in decision["resolved_addresses"]:
        try:
            with socket.create_connection((address, port), timeout=timeout):
                attempts.append({"address": address, "port": port, "connected": True})
        except OSError as exc:
            attempts.append({"address": address, "port": port, "connected": False,
                             "error": type(exc).__name__})
    return {"decision": decision, "attempts": attempts,
            "connected": any(x["connected"] for x in attempts)}
