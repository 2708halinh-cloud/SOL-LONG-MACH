#!/usr/bin/env python3
"""@Remote Desktop Connection: DNS -> RDP TCP probe -> optional mstsc profile.

Works without OpenAI or Desktop Commander. Never guesses Windows IP, opens
an inbound port, changes DNS, or stores passwords.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import socket

PRIMARY = "gambbrazil-sol100726.is"
LAN_FALLBACK = "192.168.1.12"
PORT = 3389


def probe(host: str, port: int = PORT, timeout: float = 1.2) -> dict:
    result = {"computer": host, "port": port, "dns": "UNRESOLVED", "ips": [],
              "rdp_tcp": "NOT_CONNECTED"}
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        ips = sorted({item[4][0] for item in infos})
    except OSError:
        return result
    result.update(dns="RESOLVED", ips=ips)
    for ip in ips:
        family = socket.AF_INET6 if ":" in ip else socket.AF_INET
        try:
            with socket.socket(family, socket.SOCK_STREAM) as conn:
                conn.settimeout(timeout)
                if conn.connect_ex((ip, port)) == 0:
                    result.update(rdp_tcp="TCP_CONNECTED", connected_ip=ip)
                    break
        except OSError:
            pass
    return result


def profile_text(host: str, port: int = PORT) -> str:
    if any(c in host for c in "\r\n\x00") or not host.strip():
        raise ValueError("Invalid RDP computer")
    # Standard mstsc .rdp properties. Credentials are entered interactively.
    return "\n".join([
        "screen mode id:i:2",
        "use multimon:i:0",
        "desktopwidth:i:1280",
        "desktopheight:i:800",
        "session bpp:i:32",
        f"full address:s:{host}:{port}",
        "prompt for credentials:i:1",
        "authentication level:i:2",
        "enablecredsspsupport:i:1",
        "gatewayusagemethod:i:0",
        "redirectclipboard:i:1",
        "redirectdrives:i:0",
        "redirectprinters:i:0",
        ""
    ])


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="SOL RDP route; no credential storage")
    parser.add_argument("--computer", default=PRIMARY)
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument("--timeout", type=float, default=1.2)
    parser.add_argument("--profile", type=Path, help="Write .rdp file at the named path")
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error("--port outside TCP range")
    route = probe(args.computer, args.port, args.timeout)
    if args.profile:
        args.profile.parent.mkdir(parents=True, exist_ok=True)
        args.profile.write_text(profile_text(args.computer, args.port), encoding="ascii")
        route["profile_written"] = str(args.profile)
        route["profile_is_live_connection"] = False
    print(json.dumps(route, ensure_ascii=False, sort_keys=True))
    return 0 if route["rdp_tcp"] == "TCP_CONNECTED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
