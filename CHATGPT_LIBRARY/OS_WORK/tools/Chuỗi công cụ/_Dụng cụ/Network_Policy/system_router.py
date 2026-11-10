#!/usr/bin/env python3
"""SOL System_Router: deterministically classify user-owned Windows network routes.

No network/DNS request, firewall change, remote command or process is executed.
Windows enforcement is a separate host-bound operation with exact readback.
"""
from __future__ import annotations
import argparse
import ipaddress
import json
from pathlib import Path
from urllib.parse import urlsplit

CONFIG = Path(__file__).with_name("SYSTEM_ROUTER_CURRENT.json")


def load(path: Path = CONFIG) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "SOL_SYSTEM_ROUTER/1.0":
        raise ValueError("SYSTEM_ROUTER_SCHEMA_MISMATCH")
    if data["severity"] != {"light": "WARN", "severe": "BLOCK"}:
        raise ValueError("SYSTEM_ROUTER_LEVELS_MISMATCH")
    return data


def normalize_host(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("DESTINATION_REQUIRED")
    text = value.strip()
    host = urlsplit(text).hostname if "://" in text else text
    if host is None:
        raise ValueError("INVALID_DESTINATION")
    host = host.strip().rstrip(".").lower()
    if not host or any(ch.isspace() for ch in host) or "/" in host or "*" in host:
        raise ValueError("INVALID_DESTINATION")
    try:
        return str(ipaddress.ip_address(host))
    except ValueError:
        if ":" in host:  # unbracketed host:port is not an explicit host
            raise ValueError("INVALID_DESTINATION")
        return host


def decide(destination: str, severity: str, policy: dict) -> dict:
    if severity not in policy["severity"]:
        raise ValueError("UNKNOWN_SEVERITY")
    host = normalize_host(destination)
    try:
        is_ip = ipaddress.ip_address(host)
    except ValueError:
        is_ip = None
    roots = policy["rules"]["dns_roots"]
    matched = next((r for r in roots if not is_ip and (host == r or host.endswith("." + r))), None)
    if is_ip:
        matched = next((r for r in policy["rules"]["explicit_ip_addresses"] if host == r), None)
    action = policy["severity"][severity] if matched else "NO_MATCH"
    if host == "127.0.0.1":
        relation = "THIS_DEVICE_LOOPBACK_ONLY"
    elif host.endswith("." + policy["hostinger"]["zone"]) or host == policy["hostinger"]["zone"]:
        relation = "HOSTINGER_AUTHORITATIVE_ZONE_NOT_RECURSIVE_RESOLVER"
    else:
        relation = "HOST_OR_IP_DESTINATION"
    return {
        "host": host, "severity": severity, "rule": matched,
        "action": action, "relation": relation,
        "windows_host_policy_applied": False,
        "windows_effective_enforcement": policy["status"],
        "dynamic_ips_comprehensively_blocked": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("destination")
    p.add_argument("--severity", choices=["light", "severe"], default="light")
    a = p.parse_args()
    print(json.dumps(decide(a.destination, a.severity, load()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()