#!/usr/bin/env python3
"""Append-only continuation of the existing 2026-10-20 SOL AGENT-SUB workers.

Reuse canonical 6 worker source checks. Never overwrite the original receipts.
Launch each worker in an independent Python process; cap simultaneous workers to 3.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import sol_agent_sub_parallel_archive as original

ORIGINAL_HOME = original.HOME
RUNS = ORIGINAL_HOME / "RUNS"
SOURCE_SCRIPT = Path(original.__file__).resolve()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def child(label: str, run_directory: Path) -> dict:
    command = [
        sys.executable, "-B", "-c",
        "import sys; from pathlib import Path; "
        "sys.path.insert(0,sys.argv[1]); "
        "import sol_agent_sub_parallel_archive as m; "
        "m.HOME=Path(sys.argv[2]);m.worker(sys.argv[3])",
        str(SOURCE_SCRIPT.parent), str(run_directory), label,
    ]
    started = time.monotonic()
    try:
        result = subprocess.run(
            command, cwd=str(SOURCE_SCRIPT.parent),
            stdin=subprocess.DEVNULL, capture_output=True,
            text=True, timeout=40, shell=False,
            encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return {"worker": label, "status": "TIMEOUT", "source_readback": False}
    path = run_directory / (label + ".json")
    if result.returncode != 0 or not path.is_file():
        return {"worker": label, "status": "FAILED",
                "exit_code": result.returncode, "source_readback": False}
    parsed = json.loads(path.read_text("utf-8"))
    if parsed["agent"]["AGENT_ID"] != "SOL_SUB_" + label:
        raise ValueError("worker identity mismatch")
    return {"worker": label, "status": parsed["agent"]["STATE"],
            "source_count": len(parsed["evidence"]["sources"]),
            "source_readback": parsed["evidence"]["readback"],
            "receipt_sha256": sha_file(path),
            "seconds": round(time.monotonic() - started, 3)}


def main() -> None:
    prior = ORIGINAL_HOME / "CURRENT.json"
    prior_hash = sha_file(prior) if prior.is_file() else None
    RUNS.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:10]
    run_path = RUNS / run_id
    run_path.mkdir(exist_ok=False)
    begin = time.monotonic()
    by_name = {}
    with ThreadPoolExecutor(max_workers=3, thread_name_prefix="SOL_AGENT_SUB") as pool:
        pending = {pool.submit(child, label, run_path): label for label in original.WORK}
        for future in as_completed(pending):
            label = pending[future]
            try:
                by_name[label] = future.result()
            except Exception as error:
                by_name[label] = {"worker": label, "status": "FAILED",
                                  "error_type": type(error).__name__,
                                  "source_readback": False}
    results = [by_name[label] for label in original.WORK]
    receipt = {
        "schema": "SOL_AGENTS_SUB_APPEND_ONLY_CONTINUATION/1.0",
        "run_id": run_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "ancestor_receipt": str(prior),
        "ancestor_receipt_sha256": prior_hash,
        "canonical_worker_source": str(SOURCE_SCRIPT),
        "canonical_worker_sha256": sha_file(SOURCE_SCRIPT),
        "workers_requested": len(original.WORK),
        "maximum_simultaneous_worker_processes": 3,
        "elapsed_seconds": round(time.monotonic() - begin, 3),
        "children": results,
        "all_six_attempted": len(results) == 6,
        "old_current_preserved": (
            sha_file(prior) == prior_hash if prior_hash else not prior.exists()),
        "read_only_canonical_sources": True,
        "no_task_marked_done_from_this_run": True,
    }
    target = run_path / "RUN_RECEIPT.json"
    with target.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        stream.flush()
    exact = json.loads(target.read_text("utf-8"))
    if exact != receipt or not receipt["old_current_preserved"]:
        raise RuntimeError("continuity receipt verification failed")
    print(json.dumps({
        "run_id": run_id, "receipt": str(target),
        "receipt_sha256": sha_file(target),
        "ancestor_unchanged": receipt["old_current_preserved"],
        "actual_worker_processes_attempted": len(results),
        "maximum_concurrent_workers": 3,
        "states": [{k:v for k,v in item.items() if k in ("worker","status","source_readback")}
                   for item in results],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
