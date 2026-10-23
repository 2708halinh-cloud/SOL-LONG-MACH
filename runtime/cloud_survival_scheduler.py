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


# AISSTANGT MANAGE existing real n8n agent IDs; assignment != running.
# All current IDs are literal canonical OPEN ledger IDs, not invented task instances.
SUBAGENT_ROUTES = {
 "SENSORY": {
  "agent_id":"DEYtBtOQseTBhVHS",
  "task_ids":(
   "STAMP_TRIAD_LIVE_PARTICIPATION_AND_C_DRIVE_RELIEF_20261023",
   "NEXTDNS_ED8A26","NEXTDNS_F9C9F9","HOSPOSIK_DOMAIN_MEMORY_RUNTIME",
   "SOL_LOCAL_WSL_MCP_BRIDGE","MODUAL_SENSOR_LOGS_ROUTING",
   "SOL_CHAT_BROWSER_MCP_FILE","WINDOWS_RECOVERY_DISK_SPACE",
   "ANDROID_OLLAMA_LOCALHOST_CHAT_UI") },
 "INTEGRITY": {
  "agent_id":"ilcqwLMNUdrWjvrL",
  "task_ids":(
   "SUPER_R014_SUBSCRIBE_RESET_DIRECT_20261023",
   "HELLOCHECK_GO_TESTNET_R014_20261023","TESSERACT_REAL_BOOT",
   "GOOGLE_CLOUD_ACTIONS_SECRET","TESSERACT_BOOT_AGENT_ROUTE",
   "CODEX_SECRET_RUNTIME_VERSIONS") },
 "OPEN_ROUTER": {
  "agent_id":"eT5YnxcWNGLRZ8z8",
  "task_ids":(
   "CLOUD_UNIVERSAL","WORKSPACE_32GB_DURABLE",
   "INHERITED_TESSERACT_DESKTOP","HISTORICAL_BACKLOG_IMPORT",
   "SOL_PLUGIN_CONSOLIDATION","GITHUB_COPILOT_SPACE",
   "SITES_SOL100726_REDIRECTS","TESSERACT_ART_ACTIVE_TEST_AND_6D_INTEGRATION_20261023") },
 "READBACK": {
  "agent_id":"bwjoN3TfQ8Ao717P",
  "task_ids":(
   "CODEX_CONFIG_PRIVATE_BACKUP","LIBRARY_CROSS_PROVIDER_SYNC",
   "SOL_SOURCE_12_CARRIERS","SOURCE_MATRIX_STONES_CROSS_SYNC",
   "SIX_PROJECTIONS_ENVIRONMENT_REGISTRY") }
}
ORCHESTRATOR_N8N_ID="PF4LvfkI51NJjGZS"

def reconcile_agent_tasks(ledger):
    """Read all OPEN source IDs; emit per-item provider-facing routing state.
    This is REAL routing material in a running GitHub Actions process, not proof
    that any unauthenticated n8n draft Agent has executed a model turn.
    """
    ids=[str(t["id"]) for t in ledger["tasks"]]
    if len(ids)!=len(set(ids)): raise ValueError("DUPLICATE_OPEN_TASK_ID")
    allocated={}
    for role,spec in SUBAGENT_ROUTES.items():
        for item_id in spec["task_ids"]:
            if item_id in allocated: raise ValueError("MULTIPLE_SUBAGENT_OWNERS_FOR_TASK")
            allocated[item_id]=(role,spec["agent_id"])
    missing=set(ids)-set(allocated)
    stale=set(allocated)-set(ids)
    if missing or stale:
        raise ValueError("OPEN_TASK_ROUTING_DIVERGENCE missing=%r stale=%r"%(sorted(missing),sorted(stale)))
    return [{"task_id":item_id,"status":next(t["status"] for t in ledger["tasks"] if t["id"]==item_id),
             "capability_offer":{"role":allocated[item_id][0],"n8n_agent_id":allocated[item_id][1],
                                 "n8n_runtime":"DRAFT_MISSING_MODEL_AND_CREDENTIAL"},
             "cloud_fallback":"GITHUB_ACTIONS_AND_CURRENT_PROVIDER_WHEN_CALLABLE",
             "source_task_closed":False,
             "stamp_beta_is_realized":False} for item_id in ids]

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
    import sys
    if str(root) not in sys.path:
        sys.path.insert(0,str(root))
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
    # Validate every current source task; ledger size is not a routing contract.
    if data["tasks"]:
        for item in data["tasks"]:
            if not item.get("assigned_subagent") or not item.get("assigned_agent_id"):
                raise ValueError("OPEN_TASK_WITHOUT_ASSIGNED_AGENT:"+str(item.get("id")))
            if item.get("real_execution_status") == "COMPLETED":
                raise ValueError("TASK_CLOSED_WITHOUT_VERIFIED_CONSEQUENCE:"+str(item.get("id")))
    appended=[s for s in CURRENT_SIGNALS if s["id"] not in present]
    return data,states,appended

def actual_task_selection(ledger, run_id):
    """Choose the current callable edge without waking the user's Windows.
    This selection changes what the hosted executor does; it does not close tasks.
    """
    items=ledger["tasks"]
    host_sensitive=("WINDOWS","NEXTDNS","TESSERACT_REAL_BOOT","LOCAL_WSL",
                    "ANDROID_OLLAMA","VHDX","BOOT_AGENT")
    user_priorities=("WINDOWS_RECOVERY_DISK_SPACE",
                     "SUPER_R014_SUBSCRIBE_RESET_DIRECT_20261023",
                     "HELLOCHECK_GO_TESTNET_R014_20261023")
    by_id={t.get("id"):t for t in items}
    priority=[by_id[key] for key in user_priorities if key in by_id]
    eligible=[t for t in items if
              t not in priority and not any(k in str(t.get("id","")) for k in host_sensitive)]
    # Integer run IDs on GitHub produce a stable rotating slot. On manual
    # nonnumeric invocation, use zero. No provider writes are triggered here.
    slot=int(run_id) if str(run_id).isdigit() else 0
    next_task=eligible[slot % len(eligible)] if eligible else None
    selection=[{"id":t["id"],
                "agent_id":t.get("assigned_agent_id"),
                "subagent":t.get("assigned_subagent"),
                "callability":"HOST_READBACK_REQUIRED" if t["id"]=="WINDOWS_RECOVERY_DISK_SPACE"
                              else "GITHUB_SOURCE_ONLY" if t["id"] in
                              ("SUPER_R014_SUBSCRIBE_RESET_DIRECT_20261023",
                               "HELLOCHECK_GO_TESTNET_R014_20261023")
                              else "PROVIDER_SCOPE_CHECK_REQUIRED"}
               for t in priority]
    if next_task:
        selection.append({"id":next_task["id"],
                          "agent_id":next_task.get("assigned_agent_id"),
                          "subagent":next_task.get("assigned_subagent"),
                          "callability":"PROVIDER_SCOPE_CHECK_REQUIRED"})
    return selection

def verify_hellocheck_source(root):
    """Directly check current Go source and configured TestNet network.
    A source checksum is NOT a signed or broadcast blockchain transaction.
    """
    paths=("integrations/hellocheck/go.mod",
           "integrations/hellocheck/transaction.go",
           "integrations/hellocheck/rpc.go",
           "integrations/hellocheck/cmd/hellocheck/main.go")
    snapshots=[fingerprint(root,x) for x in paths]
    if not all(x["exists"] for x in snapshots):
        return {"passed":False,"reason":"HELLOCHECK_GO_SOURCE_MISSING"}
    rpc=(root/paths[2]).read_text(encoding="utf-8")
    passed=all(x in rpc for x in ("getblockchaininfo","sendrawtransaction",
                                  'chain.Chain!="test"', 'chain.Chain!="testnet4"'))
    return {"passed":passed,
            "source_paths":snapshots,
            "real_testnet_transaction_broadcast":False,
            "rpc_secrets_in_artifact":False}

def build(root,now,run_id,sha):
    ledger,states,appended=classify_open_ledger(root)
    routing=reconcile_agent_tasks(ledger)
    sources=[fingerprint(root,SOURCE_LEDGER)]
    for _,names in CLOUD_CHECKS:
        sources.extend(fingerprint(root,name) for name in names)
    c_free_percent=round(100*KNOWN_CRITICAL_C_SPACE_BYTES/KNOWN_C_CAPACITY_BYTES,3)
    cloud_actions={
       "ER_SQL_SCHEMA":probe_er_schema(root),
       "R014_RESPONSE_REGRESSION":verify_r014(root),
       "THIT_THO_CONTRACTS":verify_contracts(root),
       "T005_HELLOHABIT_ANDROID":verify_t005(root),
       "HELLOCHECK_GO_TESTNET_SOURCE":verify_hellocheck_source(root),
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
                    "live_subagent_selection":actual_task_selection(ledger,run_id),
                    "permission_policy":"HIGHEST_GRANTED_PERSONAL_CONNECTOR_WITHIN_AUTHORIZED_SCOPE",
                    "subagent_offer_routes":routing,
                    "routes_cover_all_source_tasks":len(routing)==len(ledger["tasks"]),
                    "n8n_agents_autonomously_executed":False,
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
