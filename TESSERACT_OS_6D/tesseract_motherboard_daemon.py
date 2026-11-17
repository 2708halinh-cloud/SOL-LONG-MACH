"""Bounded TESSERACT motherboard continuity/health loop.

The daemon restores durable state each cycle, emits a fresh heartbeat and records open work.
It does not execute arbitrary pending actions without a registered, authorized executor.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import time
from pathlib import Path

try:
    from .tesseract_motherboard_kernel import MotherboardKernel
except ImportError:
    from tesseract_motherboard_kernel import MotherboardKernel

_shutdown = False


def _request_shutdown(_signum, _frame):
    global _shutdown
    _shutdown = True


def run(root: Path, interval: float, once: bool = False) -> int:
    global _shutdown
    interval = max(1.0, float(interval))
    state_dir = root / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    pid_path = state_dir / "tesseract_motherboard_daemon.pid"
    heartbeat_path = state_dir / "tesseract_motherboard_daemon_heartbeat.json"
    stop_path = state_dir / "TESSERACT_MOTHERBOARD_DAEMON.STOP"
    pid_path.write_text(str(os.getpid()) + "\n", encoding="utf-8")
    signal.signal(signal.SIGINT, _request_shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _request_shutdown)
    kernel = MotherboardKernel(root)
    try:
        while not _shutdown:
            if stop_path.exists():
                stop_path.unlink()
                break
            cycle = kernel.run_cycle(heartbeat_path)
            print(json.dumps(cycle, ensure_ascii=False, sort_keys=True), flush=True)
            if once:
                break
            # Bounded cycle + sleep: no busy-spin and no false claim of work completion.
            deadline = time.monotonic() + interval
            while not _shutdown and time.monotonic() < deadline:
                if stop_path.exists():
                    stop_path.unlink()
                    _request_shutdown(None, None)
                    break
                time.sleep(min(0.25, max(0.01, deadline - time.monotonic())))
    finally:
        try:
            if pid_path.exists() and pid_path.read_text(encoding="utf-8").strip() == str(os.getpid()):
                pid_path.unlink()
        except OSError:
            pass
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="TESSERACT motherboard continuity and process monitor")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent),
                        help="runtime root; checkpoint and heartbeat live under root/state")
    parser.add_argument("--interval", type=float, default=5.0, help="seconds between bounded cycles")
    parser.add_argument("--once", action="store_true", help="execute one verification cycle and exit")
    args = parser.parse_args()
    return run(Path(args.root), args.interval, args.once)


if __name__ == "__main__":
    raise SystemExit(main())