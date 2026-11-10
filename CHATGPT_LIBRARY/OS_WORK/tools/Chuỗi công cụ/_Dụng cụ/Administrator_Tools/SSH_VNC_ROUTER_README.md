# SOL Administrator Tools — SSH/VNC Router · Termux ARM64

## Runtime verified (2026-10-17)

- Real device: Desktop Commander `localhost`, device ID `982bb1fa-a3e1-470d-bbd8-7957b1f195f4`, Termux user `u0_a579`.
- Canonical source on device: `/data/data/com.termux/files/home/SOL_TOOLS/Remote_Desktop_Connection/ssh_vnc_router.py`.
- Test script: `test_ssh_vnc_router.py` in the same folder.
- Library carrier: `SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/Chuỗi công cụ/_Dụng cụ/Administrator_Tools/`.
- Architecture: **AGENT → Router → SSH (command execution) / VNC-over-SSH (GUI on demand)**. A model is a tool used by the agent, not the agent's identity.

## Observed operational verification

1. SSH executable, daemon and keygen installed; TigerVNC and tmux installed.
2. Generated a private SSH key **on the Android device only**, added its public key to Termux `authorized_keys` (0600); server config enforces **publickey authentication**, `PasswordAuthentication no`, `AllowTcpForwarding local`, `GatewayPorts no`.
3. Started an isolated `sshd` bound to `127.0.0.1:8022` and executed a real SSH command: `SOL_SSH_PROBE_OK`, exit code 0.
4. Started TigerVNC `:1` with existing user-configured VNC password and `-localhost yes`.
5. Opened a real SSH local tunnel `127.0.0.1:15901 → SSH → 127.0.0.1:5901` and received `RFB 003.008` through that tunnel.
6. Stopped the router-owned VNC session; port 5901 became closed; SSH continued to pass authentication.
7. On-device `unittest` fresh run: **12 tests, OK**, exit code 0. Verification date: 2026-10-17.
8. Original source copies match hashes shown in the manifest, `sha256` computed on Termux and independently on local files.

## Commands on Termux

```sh
cd "$HOME/SOL_TOOLS/Remote_Desktop_Connection"
python3 ssh_vnc_router.py status
python3 ssh_vnc_router.py route --kind read   # direct file tool, do not launch remote sessions
python3 ssh_vnc_router.py route --kind shell  # SSH plan, no GUI
python3 ssh_vnc_router.py ssh-probe            # actual authenticated SSH command
python3 ssh_vnc_router.py route --kind gui    # GUI plan only, no session started
python3 ssh_vnc_router.py route --kind gui --activate  # start on-demand TigerVNC
python3 ssh_vnc_router.py vnc-stop            # release GUI resources
python3 -m unittest -v test_ssh_vnc_router.py
```

The local tunnel command (on the device for smoke-test) uses an on-device private key that is **not included** in any exported file. For a separate client machine, enroll **that client's public key** via an authorized channel first; never export the device's private key to a shared library. Keep the TigerVNC listener on loopback. Wi-Fi IP `192.168.1.12` was supplied by the user, but the router was deliberately activated on loopback and there is no verified Windows client connection from this run.

## Resource and safety policy

- Pure data/file tasks use Desktop Commander file tools; do not start SSH/VNC unless the operation benefits.
- CLI/background command workloads: SSH; if SSH is already running, reuse it.
- GUI only: TigerVNC over SSH tunnel, start when requested, stop after use.
- Do not disable authentication; do not publish port 5901 to LAN; do not turn on GUI at boot.
- No root, Docker daemon, disk formatting, removal, system reinstall, user-folder deletion, or background monitoring tasks created by this router.
- If Desktop Commander connection is offline, report only the last verified state; it is not evidence that the service is still running.

## READBACK → NEXT

Next actor action on a GUI request: execute `route --kind gui --activate`, verify SSH and RFB handshake, perform the requested GUI work, then `vnc-stop`. On a shell request: reuse SSH and keep VNC inactive. On an external-client request: verify that client's public key and local interface bind before allowing LAN reachability.