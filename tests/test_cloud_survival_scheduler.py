"""Independent cloud survival and source-preserving OPEN continuity tests."""
from __future__ import annotations
import configparser
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from runtime import cloud_survival_scheduler as survivor

ROOT=Path(__file__).resolve().parents[1]

class CloudSurvivalTests(unittest.TestCase):
    def test_all_prior_open_tasks_are_still_present(self):
        ledger,states,new=survivor.classify_open_ledger(ROOT)
        self.assertEqual(sum(states.values()),len(ledger["tasks"]))
        self.assertGreaterEqual(len(ledger["tasks"]),20)
        self.assertNotIn("DONE",states)
        self.assertTrue(any(s["id"]=="USER_DIRECT_WINDOWS_C_FULL_CRASH_20261023" for s in new))

    def test_historical_c_is_critical_and_must_not_be_claimed_fixed(self):
        self.assertLess(100*survivor.KNOWN_CRITICAL_C_SPACE_BYTES/
                        survivor.KNOWN_C_CAPACITY_BYTES,5)

    def test_cloud_source_exists_without_offline_windows(self):
        state=survivor.build(ROOT,"2026-10-23T00:00:00Z","TEST","TESTSHA")
        self.assertFalse(state["execution"]["windows_device_required"])
        self.assertFalse(state["execution"]["host_os_disk_modified"])
        self.assertFalse(state["STAMP_OLD"]["prior_disk_observation"]["live_windows_readback"])
        self.assertEqual(state["STAMP_LIVE"]["critical_windows_mode"],"HIGH_SAFETY_HOLD")
        self.assertFalse(state["STAMP_LIVE"]["host_heavy_tasks_allowed"])
        self.assertTrue(state["STAMP_BETA"]["pending_real_world_disk_recovery"])
        self.assertFalse(state["all_objectives_completed"])

    def test_actual_cloud_tasks_are_executed(self):
        state=survivor.build(ROOT,"2026-10-23T00:00:00Z","TEST","TESTSHA")
        self.assertTrue(state["STAMP_LIVE"]["cloud_actions"]["ER_SQL_SCHEMA"]["passed"])
        self.assertTrue(state["STAMP_LIVE"]["cloud_actions"]["R014_RESPONSE_REGRESSION"]["passed"])
        self.assertTrue(state["STAMP_LIVE"]["cloud_actions"]["THIT_THO_CONTRACTS"]["passed"])

    def test_all_source_open_nodes_have_single_real_subagent_route(self):
        ledger,_,_=survivor.classify_open_ledger(ROOT)
        routes=survivor.reconcile_agent_tasks(ledger)
        source_ids={item["id"] for item in ledger["tasks"]}
        routed_ids=[item["task_id"] for item in routes]
        self.assertEqual(set(routed_ids),source_ids)
        self.assertEqual(len(routed_ids),len(source_ids))
        self.assertEqual(len(routed_ids),len(set(routed_ids)))
        self.assertEqual({x["capability_offer"]["role"] for x in routes},
                         {"SENSORY","INTEGRITY","OPEN_ROUTER","READBACK"})
        for item in routes:
            self.assertFalse(item["source_task_closed"])
            self.assertFalse(item["stamp_beta_is_realized"])
            self.assertEqual(item["capability_offer"]["n8n_runtime"],
                             "DRAFT_MISSING_MODEL_AND_CREDENTIAL")

    def test_gitmodules_paths_match_tracked_gitlinks(self):
        config=configparser.ConfigParser()
        loaded=config.read(ROOT/".gitmodules",encoding="utf-8")
        self.assertTrue(loaded)
        configured={section:config[section].get("path") for section in config.sections()
                    if section.startswith('submodule "')}
        tree=subprocess.run(["git","-c","core.quotePath=false","ls-tree","-r","-z","HEAD"],
                            cwd=ROOT,check=True,capture_output=True,text=True).stdout
        gitlink_paths=set()
        for entry in tree.split("\0"):
            if not entry:
                continue
            metadata,path=entry.split("\t",1)
            if metadata.startswith("160000 commit "):
                gitlink_paths.add(path)
        self.assertTrue(configured)
        self.assertEqual(set(configured.values()),gitlink_paths)

    def test_small_ledger_is_validated_without_27_item_threshold(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            ledger_path=root/"CURRENT_RUNTIME"/"OPEN_TASKS_CURRENT.json"
            ledger_path.parent.mkdir(parents=True)
            valid_task={"id":"SMALL_TASK","status":"OPEN",
                        "assigned_subagent":"OPEN_ROUTER","assigned_agent_id":"agent-1",
                        "real_execution_status":"OPEN_NOT_PROVEN_COMPLETED"}
            ledger_path.write_text(json.dumps({"tasks":[valid_task]}),encoding="utf-8")
            ledger,states,_=survivor.classify_open_ledger(root)
            self.assertEqual([item["id"] for item in ledger["tasks"]],["SMALL_TASK"])
            self.assertEqual(states,{"OPEN":1})

            invalid_task={key:value for key,value in valid_task.items()
                          if key!="assigned_agent_id"}
            ledger_path.write_text(json.dumps({"tasks":[invalid_task]}),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,
                                        "OPEN_TASK_WITHOUT_ASSIGNED_AGENT:SMALL_TASK"):
                survivor.classify_open_ledger(root)

    def test_agent_route_rejects_missing_source_without_mutating_ledger(self):
        ledger,_,_=survivor.classify_open_ledger(ROOT)
        changed={"tasks":ledger["tasks"][:-1]}
        with self.assertRaisesRegex(ValueError,"OPEN_TASK_ROUTING_DIVERGENCE"):
            survivor.reconcile_agent_tasks(changed)

    def test_new_signals_cannot_erase_source_task_ids(self):
        ledger,_,appended=survivor.classify_open_ledger(ROOT)
        ids=[i["id"] for i in ledger["tasks"]]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertFalse(set(x["id"] for x in appended).intersection(ids))

if __name__=="__main__":unittest.main()
