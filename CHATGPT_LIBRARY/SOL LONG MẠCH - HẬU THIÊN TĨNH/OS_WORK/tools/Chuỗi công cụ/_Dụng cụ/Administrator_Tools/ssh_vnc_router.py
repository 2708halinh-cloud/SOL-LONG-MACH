#!/usr/bin/env python3
"""SOL SSH/VNC Router (Termux). No Docker, root, password export or destructive action.

Command-only workloads use SSH; GUI uses TigerVNC over an SSH tunnel.
Status is side-effect free. VNC starts only on explicit activation.
"""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

HOME = Path.home()
DIR = HOME / "SOL_TOOLS" / "Remote_Desktop_Connection"
STATE = DIR / ".ssh_vnc_router"
SSH_DIR = HOME / ".ssh"
PORT = 8022
DISPLAY = ":1"
VNC_PORT = 5901
KEY = SSH_DIR / "sol_router_ed25519"
AUTHORIZED = SSH_DIR / "authorized_keys"
PREFIX = Path(os.environ.get("PREFIX", "/data/data/com.termux/files/usr"))


def run(argv, *, timeout=12):
    return subprocess.run(argv, text=True, capture_output=True, timeout=timeout, check=False)


def tcp_open(host, port):
    try:
        with socket.create_connection((host, port), timeout=0.4):
            return True
    except (OSError, TimeoutError):
        return False


def status():
    ssh_local = tcp_open("127.0.0.1", PORT)
    vnc_local = tcp_open("127.0.0.1", VNC_PORT)
    return {"schema": "SOL_SSH_VNC_ROUTER/1.0",
            "home": str(HOME), "ssh": {"port": PORT, "local_open": ssh_local,
            "key_exists": KEY.is_file(), "auth_keys_exists": AUTHORIZED.exists()},
            "vnc": {"display": DISPLAY, "port": VNC_PORT,
            "localhost_open": vnc_local, "router_owned": (STATE / "vnc_owned").exists()},
            "policy": "SSH_KEY_ONLY_VNC_LOOPBACK_ON_DEMAND",
            "no_automatic_vnc": True, "no_root": True}


def write_secure(path, content, perm=0o600):
    path.write_text(content, encoding="utf-8")
    path.chmod(perm)


def init_key():
    SSH_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    SSH_DIR.chmod(0o700)
    STATE.mkdir(mode=0o700, parents=True, exist_ok=True)
    if not KEY.exists():
        p = run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(KEY),
                 "-C", "SOL_ROUTER_TERMUX_LOCAL"], timeout=20)
        if p.returncode:
            raise RuntimeError("SSH_KEYGEN_FAILED: " + p.stderr[-350:])
    KEY.chmod(0o600)
    pub = KEY.with_suffix(".pub").read_text().strip()
    original = AUTHORIZED.read_text() if AUTHORIZED.exists() else ""
    pub_fingerprint = pub.split()
    if len(pub_fingerprint) < 2:
        raise RuntimeError("BAD_SSH_PUBLIC_KEY")
    if pub_fingerprint[1] not in original:
        with AUTHORIZED.open("a", encoding="utf-8") as f:
            f.write(("" if not original or original.endswith("\n") else "\n")
                    + "no-agent-forwarding,no-X11-forwarding,no-user-rc " + pub + "\n")
    AUTHORIZED.chmod(0o600)


def valid_bind(address):
    if address == "127.0.0.1":
        return address
    ip = ipaddress.ip_address(address)
    if ip.version != 4 or not ip.is_private or ip.is_loopback:
        raise ValueError("SSH_BIND_MUST_BE_LOOPBACK_OR_PRIVATE_IPV4")
    with socket.socket() as s:
        s.bind((address, 0))  # check that this interface belongs to this device
    return address


def start_ssh(bind):
    bind = valid_bind(bind)
    if tcp_open(bind, PORT):
        return {"status": "ALREADY_RUNNING", "bind": bind, "port": PORT}
    if tcp_open("127.0.0.1", PORT):
        return {"status": "PORT_IN_USE", "bind": bind, "port": PORT}
    init_key()
    conf = STATE / "router_sshd.conf"
    host = PREFIX / "etc" / "ssh" / "ssh_host_ed25519_key"
    if not host.exists():
        raise RuntimeError("SSHD_HOST_KEY_ABSENT")
    lines = [
        "Port " + str(PORT),
        "ListenAddress " + bind,
        "HostKey " + str(host),
        "AuthorizedKeysFile " + str(AUTHORIZED),
        "PidFile " + str(STATE / "sshd.pid"),
        "PasswordAuthentication no",
        "KbdInteractiveAuthentication no",
        "PubkeyAuthentication yes",
        "AuthenticationMethods publickey",
        "PermitRootLogin no",
        "AllowTcpForwarding local",
        "GatewayPorts no",
        "X11Forwarding no",
        "StrictModes yes",
        "LogLevel ERROR",
        "UsePAM no",
    ]
    write_secure(conf, "\n".join(lines) + "\n")
    checked = run(["sshd", "-t", "-f", str(conf)])
    if checked.returncode:
        raise RuntimeError("SSHD_CONFIG_TEST_FAILED: " + checked.stderr[-300:])
    started = run(["sshd", "-f", str(conf), "-E", str(STATE / "sshd.log")])
    if started.returncode:
        raise RuntimeError("SSHD_START_FAILED: " + started.stderr[-300:])
    for _ in range(12):
        if tcp_open(bind, PORT):
            return {"status": "RUNNING", "bind": bind, "port": PORT,
                    "auth": "publickey_only", "password_auth": False,
                    "private_key_path": str(KEY), "vnc_exposed_to_lan": False}
        time.sleep(0.15)
    raise RuntimeError("SSHD_NOT_LISTENING_AFTER_START")


def probe_ssh(host):
    args = ["ssh", "-i", str(KEY), "-p", str(PORT),
            "-o", "BatchMode=yes", "-o", "ConnectTimeout=3",
            "-o", "StrictHostKeyChecking=accept-new",
            "-o", "UserKnownHostsFile=" + str(STATE / "known_hosts"),
            "-o", "IdentitiesOnly=yes",
            f"{os.environ.get('USER', 'u0_a579')}@{host}",
            "printf SOL_SSH_PROBE_OK"]
    if not KEY.exists():
        raise RuntimeError("SSH_KEY_NOT_INITIALIZED")
    p = run(args, timeout=8)
    return {"host": host, "port": PORT, "ssh_authenticated": p.returncode == 0
            and "SOL_SSH_PROBE_OK" in p.stdout,
            "exit_code": p.returncode,
            "result": p.stdout.strip()[-80:], "error": p.stderr.strip()[-180:]}


def start_vnc():
    if tcp_open("127.0.0.1", VNC_PORT):
        return {"status": "ALREADY_RUNNING", "port": VNC_PORT, "router_started": False}
    if not (HOME / ".vnc" / "passwd").is_file():
        raise RuntimeError("VNC_PASSWORD_FILE_ABSENT")
    STATE.mkdir(mode=0o700, parents=True, exist_ok=True)
    p = run(["vncserver", DISPLAY, "-localhost", "yes", "-geometry", "1024x600",
             "-depth", "16"], timeout=24)
    if p.returncode and not tcp_open("127.0.0.1", VNC_PORT):
        raise RuntimeError("VNC_START_FAILED: " + (p.stderr + p.stdout)[-450:])
    for _ in range(12):
        if tcp_open("127.0.0.1", VNC_PORT):
            write_secure(STATE / "vnc_owned", "display=:1\nlocalhost_only=true\n")
            return {"status": "RUNNING", "display": DISPLAY,
                    "port": VNC_PORT, "localhost_only": True,
                    "transport": "SSH_LOCAL_FORWARD"}
        time.sleep(0.2)
    raise RuntimeError("VNC_NOT_LISTENING_AFTER_START")


def stop_vnc():
    marker = STATE / "vnc_owned"
    if not marker.exists():
        return {"status": "NOT_ROUTER_OWNED", "stopped": False}
    p = run(["vncserver", "-kill", DISPLAY], timeout=12)
    if tcp_open("127.0.0.1", VNC_PORT):
        raise RuntimeError("VNC_STILL_RUNNING: " + p.stderr[-200:])
    marker.unlink()
    return {"status": "STOPPED", "stopped": True, "memory_policy": "VNC_ON_DEMAND"}


def plan(kind, activate=False, bind="127.0.0.1"):
    if kind not in ("read", "shell", "gui"):
        raise ValueError("INVALID_KIND")
    route = "DESKTOP_COMMANDER_FILE_READ" if kind == "read" else (
        "SSH_COMMAND_ONLY" if kind == "shell" else "VNC_OVER_SSH_TUNNEL")
    result = {"task_kind": kind, "route": route, "gui_started_automatically": False,
              "requires_vnc": kind == "gui", "activation": activate,
              "tunnel": f"ssh -N -L 5901:127.0.0.1:5901 -p {PORT} user@{bind}",
              "ssh_private_key_local_path": str(KEY),
              "external_client_private_key_transfer": False}
    if activate and kind in ("shell", "gui"):
        result["ssh"] = start_ssh(bind)
    if activate and kind == "gui":
        result["vnc"] = start_vnc()
    result["observed"] = status()
    return result


def main():
    parser = argparse.ArgumentParser(description="SOL SSH/VNC resource-aware Termux router")
    parser.add_argument("action", choices=["status", "ssh-start", "ssh-probe",
                                          "vnc-start", "vnc-stop", "route"])
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--kind", choices=["read", "shell", "gui"], default="read")
    parser.add_argument("--activate", action="store_true")
    args = parser.parse_args()
    try:
        out = {"status": status()} if args.action == "status" else (
            {"ssh": start_ssh(args.bind)} if args.action == "ssh-start" else (
            {"probe": probe_ssh(args.bind)} if args.action == "ssh-probe" else (
            {"vnc": start_vnc()} if args.action == "vnc-start" else (
            {"vnc": stop_vnc()} if args.action == "vnc-stop" else
            plan(args.kind, args.activate, args.bind)))))
        print(json.dumps(out, ensure_ascii=False, indent=2))
        if args.action == "ssh-probe" and not out["probe"]["ssh_authenticated"]:
            return 2
        return 0
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "BLOCK", "reason": str(exc),
                          "next_actor": "AGENT", "no_destructive_actions": True}))
        return 2


if __name__ == "__main__":
    sys.exit(main())