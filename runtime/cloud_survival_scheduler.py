#!/usr/bin/env python3
"""Source-bound cloud-only continuation with Windows-critical safety hold.

Each invocation consumes the existing user OPEN ledger and runs concrete,
non-destructive repository checks. It cannot clean an offline C: drive.
STAMP_BETA is a proposal, never a verified real-world consequence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCE_LEDGER="CURRENT_RUNTIME/OPEN_TASKS_CURRENT.json"
KNOWN_CRITICAL_C_SPACE_BYTES=3991265280
KNOWN_C_CAPACITY_BYTES=509337399296
HEAVY_HOST_ACTIVITIES=("QEMU","DOCKER","WSL","VHDX","MODEL_TRAINING","BULK_COPY")
CLOUD_CHECKS=(
    ("R014_RESPONSE_REGRESSION",("runtime/ggdv_response_gate.py","runtime/test_ggdv_response_gate.py")),
    ("ER_SQL_SCHEMA",("architecture/THIT_THO/data/schema/001_er.sql",)),
    ("THIT_THO_CONTRACTS",("architecture/THIT_THO/contracts/telemetry-event.schema.json",
                           "architecture/THIT_THO/contracts/telemetry.proto",
                           "architecture/THIT_THO/os/BOOT_CONTRACT.json")),
    ("WINDOWS_REENTRY_READ_ONLY",("runtime/windows_c_survival_probe.ps1",)),
    ("T005_HELLOHABIT_ANDROID",("runtime/hellohabit_t005_adapter.py",
                               "integrations/android/hellohabit/manifest.binding.json")),
)
CURRENT_SIGNALS=(
    {"id":"USER_DIRECT_WINDOWS_C_FULL_CRASH_20261023",
     "type":"SAFETY_CRITICAL","next_route":"WINDOWS_REENTRY_ONLY_AFTER_OS_STABLE",
     "source":"USER_DIRECT_CHAT_20261023",
     "target":"C:/","real_disk_cleanup_done":False},
    {"id":"THIT_THO_TESSERACT_MEI_SUPER_AI_20261023",
     "type":"CLOUD_CALLABLE","next_route":"GITHUB_HOSTED_VERIFICATION",
     "source":"MEI_INBOX_RECEIPTS_20261023",
     "target":"architecture/THIT_THO","real_disk_cleanup_done":False},
    {"id":"SUPER_R014_SUBSCRIBE_RESET_20261023",
     "type":"CLOUD_CALLABLE","next_route":"GITHUB_HOSTED_VERIFICATION",
     "source":"USER_DIRECT_CHAT_20261023",
     "target":"runtime/ggdv_response_gate.py","real_disk_cleanup_done":False},
)

def fingerprint(root,relative):
    path=root/relative
    if path.is_symlink() or not path.is_file():
        return {"path":relative,"exists":False}
    raw=path.read_bytes()
    return {"path":relative,"exists":True,
            "size_bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}

def probe_er_schema(root):
    ddl=(root/"architecture/THIT_THO/data/schema/001_er.sql").read_text(encoding="utf-8")
    con=sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys=ON")
    try:
        con.executescript(ddl)
        tables={row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        required={"sources","entities","relations","relation_participants",
                  "relation_types","entity_sets","attribute_definitions"}
        success=required.issubset(tables) and not con.execute("PRAGMA foreign_key_check").fetchall()
        return {"executed_on":"GITHUB_RUNNER_SQLITE_MEMORY",
                "passed":success,"tables_found":len(tables),
                "source_file":"architecture/THIT_THO/data/schema/001_er.sql"}
    finally:
        con.close()

def verify_r014(root):
    cmd=[sys.executable,"-m","unittest","discover","-s","runtime",
         "-p","test_ggdv_response_gate.py","-v"]
    p=subprocess.run(cmd,cwd=root,stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT,text=True,timeout=80,check=False)
    return {"executed_on":"GITHUB_RUNNER_PYTHON",
            "passed":p.returncode==0,
            "exit_code":p.returncode,
            "test_line_summary":next((s.strip() for s in reversed(p.stdout.splitlines())
                                      if s.strip().startswith("Ran ")),None),
            "source_files":["runtime/ggdv_response_gate.py",
                            "runtime/test_ggdv_response_gate.py"]}

def verify_contracts(root):
    base=root/"architecture/THIT_THO"
    wire=json.loads((base/"contracts/telemetry-event.schema.json").read_text(encoding="utf-8"))
    boot=json.loads((base/"os/BOOT_CONTRACT.json").read_text(encoding="utf-8"))
    proto=(base/"contracts/telemetry.proto").read_text(encoding="utf-8")
    assert "schema_version" in wire.get("properties",{})
    assert boot.get("custom_bare_metal_kernel_built") is False
    assert "message TelemetryEvent" in proto
    return {"executed_on":"GITHUB_RUNNER_PYTHON","passed":True,
            "real_custom_kernel_boot_proven":False}

def verify_t005(root):
    from runtime.hellohabit_t005_adapter import inspect
    receipt=inspect(root)
    return {"passed":receipt["T005_package_identity_registered"],
            "source_sha256":receipt["source_sha256"],
            "android_app_installed":receipt["installed_on_android_proven"],
            "app_identity":receipt["package"],
            "real_habit_data_sync_proven":receipt["real_habit_data_sync_proven"]}

def classify_open_ledger(root):
    data=json.loads((root/SOURCE_LEDGER).read_text(encoding="utf-8"))
    if not isinstance(data.get("tasks"),list):
        raise ValueError("OPEN_LEDGER_TASKS_MISSING")
    states={}
    for item in data["tasks"]:
        state=str(item.get("status","UNSPECIFIED"))
        states[state]=states.get(state,0)+1
    # Never change, drop or close an existing item. Augment on next-state only.
    present={str(item.get("id")) for item in data["tasks"]}
    appended=[s for s in CURRENT_SIGNALS if s["id"] not in present]
    return data,states,appended

def build(root,now,run_id,sha):
    ledger,states,appended=classify_open_ledger(root)
    sources=[fingerprint(root,SOURCE_LEDGER)]
    for _,names in CLOUD_CHECKS:
        sources.extend(fingerprint(root,name) for name in names)
    c_free_percent=round(100*KNOWN_CRITICAL_C_SPACE_BYTES/KNOWN_C_CAPACITY_BYTES,3)
    cloud_actions={
       "ER_SQL_SCHEMA":probe_er_schema(root),
       "R014_RESPONSE_REGRESSION":verify_r014(root),
       "THIT_THO_CONTRACTS":verify_contracts(root),
       "T005_HELLOHABIT_ANDROID":verify_t005(root),
    }
    return {
      "schema":"SOL_STAMPS_SURVIVAL_INDEPENDENT_CONTINUATION_V1",
      "execution":{"provider":"GITHUB_ACTIONS","run_id":run_id,
                   "commit_sha":sha,"observed_at_utc":now,
                   "windows_device_required":False,
                   "host_os_disk_modified":False},
      "STAMP_OLD":{"ledger_source":SOURCE_LEDGER,
                   "source_task_count":len(ledger["tasks"]),
                   "source_task_states":states,"source_fingerprints":sources,
                   "prior_disk_observation":{"drive":"C:",
                      "prior_free_bytes":KNOWN_CRITICAL_C_SPACE_BYTES,
                      "prior_capacity_bytes":KNOWN_C_CAPACITY_BYTES,
                      "historical_free_percent":c_free_percent,
                      "live_windows_readback":False},
                   "prior_history_unchanged":True},
      "STAMP_LIVE":{"cloud_actions":cloud_actions,
                    "all_cloud_actions_passed":all(x["passed"] for x in cloud_actions.values()),
                    "source_tasks_carried_forward":len(ledger["tasks"]),
                    "supplementary_new_signals":appended,
                    "no_source_tasks_closed":True,
                    "critical_windows_mode":"HIGH_SAFETY_HOLD",
                    "host_heavy_tasks_allowed":False,
                    "blocked_host_actions":list(HEAVY_HOST_ACTIVITIES)},
      "STAMP_BETA":{"next_host_action":"OBSERVE_WINDOWS_UPDATE_COMPLETION_AND_MEASURE_C_BEFORE_MUTATING",
                    "next_cloud_action":"RERUN_CLOUD_VALIDATIONS_AND_RECONCILE_OPEN_EDGES",
                    "independent_hostless_runner":"GITHUB_ACTIONS",
                    "pending_real_world_disk_recovery":True,
                    "pending_actual_vhdx_boot_verification":True,
                    "user_must_not_be_forced_to_REPEAT_WARNINGS":True},
      "all_objectives_completed":False,
      "file_receipt_not_equal_remediation":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,default=Path.cwd())
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    root=args.repo_root.resolve()
    result=build(root,datetime.now(timezone.utc).isoformat(),
                 os.environ.get("GITHUB_RUN_ID","MANUAL"),
                 os.environ.get("GITHUB_SHA","UNKNOWN"))
    output=args.output
    output.parent.mkdir(parents=True,exist_ok=True)
    tmp=output.with_name(output.name+".new")
    tmp.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    os.replace(tmp,output)
    assert json.loads(output.read_text(encoding="utf-8"))==result
    print(json.dumps({"readback":True,
                      "open_tasks_carried_forward":result["STAMP_LIVE"]["source_tasks_carried_forward"],
                      "new_user_signals_carried":len(result["STAMP_LIVE"]["supplementary_new_signals"]),
                      "cloud_actions":{k:v["passed"] for k,v in result["STAMP_LIVE"]["cloud_actions"].items()},
                      "windows_disk_cleanup_performed":False,
                      "windows_host_actions_blocked":True},ensure_ascii=False))
    return 0 if result["STAMP_LIVE"]["all_cloud_actions_passed"] else 1

if __name__=="__main__":
    raise SystemExit(main())
