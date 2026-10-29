import json
import os
import tempfile
import unittest
from pathlib import Path

from tesseract_motherboard_kernel import (
    MotherboardKernel,
    compare_capability_regression,
    inspect_process,
    resolve_brain_label,
)


class TestTesseractMotherboardKernel(unittest.TestCase):
    def test_new_process_restores_checkpoint_and_unfinished_edges(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = MotherboardKernel(root)
            first.set_objective("OBJ-RESTORE", ["edge-a", "edge-b"])
            first.complete_edge("edge-a", receipt={"id": "r1"}, readback={"verified": True})
            second = MotherboardKernel(root)
            state = second.restore()
            self.assertEqual(state["objective_id"], "OBJ-RESTORE")
            self.assertEqual(state["unfinished_edges"], ["edge-b"])
            self.assertEqual(state["state_n_plus_1"], 1)

    def test_scheduler_enforces_cpu_memory_and_time_budget(self):
        with tempfile.TemporaryDirectory() as td:
            kernel = MotherboardKernel(Path(td))
            result = kernel.schedule(
                [{"id": "a", "cpu_ms": 10, "memory_mb": 64},
                 {"id": "b", "cpu_ms": 100, "memory_mb": 64}],
                cpu_budget_ms=20, memory_budget_mb=128, time_budget_ms=20,
            )
            self.assertEqual([x["id"] for x in result["selected"]], ["a"])
            self.assertEqual([x["id"] for x in result["deferred"]], ["b"])

    def test_tool_observation_records_evidence_without_claiming_missing_readback(self):
        with tempfile.TemporaryDirectory() as td:
            kernel = MotherboardKernel(Path(td))
            event = kernel.observe_tool(
                tool_name="example.neuron",
                action={"kind": "READ", "target": "source-a"},
                provider_receipt={"receipt_id": "R-1"},
                consequence={"observed": True},
                readback=None,
            )
            self.assertEqual(event["tool_name"], "example.neuron")
            self.assertEqual(event["verification_state"], "OPEN_READBACK")
            journal = (Path(td) / "journal" / "brainwaves.jsonl").read_text(encoding="utf-8")
            self.assertIn('"wave_band"', journal)

    def test_ububu_and_untunbu_remain_distinct_provenance_labels(self):
        ububu = resolve_brain_label("UBUBU")
        untunbu = resolve_brain_label("UNTUNBU")
        self.assertNotEqual(ububu["brain_id"], untunbu["brain_id"])
        self.assertNotEqual(ububu["canonical_label"], untunbu["canonical_label"])
        with self.assertRaises(ValueError):
            resolve_brain_label("UBUBU/UNTUNBU")

    def test_neuron_weights_are_generated_from_evidence_and_penalize_repetition(self):
        with tempfile.TemporaryDirectory() as td:
            kernel = MotherboardKernel(Path(td))
            first = kernel.update_neuron_weights(
                "github.read", category="source_read",
                progress=0.8, novelty=0.7, efficiency=0.6, risk=0.1,
                repetition=0.0, evidence_ref="receipt-1",
            )
            second = kernel.update_neuron_weights(
                "github.read", category="source_read",
                progress=0.2, novelty=0.0, efficiency=0.2, risk=0.8,
                repetition=1.0, evidence_ref="receipt-2",
            )
            self.assertNotEqual(first["weights"], second["weights"])
            self.assertLess(second["reward"], first["reward"])
            self.assertEqual(second["evidence_ref"], "receipt-2")

    def test_5d_regression_preserves_old_capabilities_and_marks_new_ones(self):
        result = compare_capability_regression(
            previous={"read_file", "search", "write_receipt"},
            current={"read_file", "search", "new_probe"},
        )
        self.assertEqual(result["preserved"], ["read_file", "search"])
        self.assertEqual(result["missing"], ["write_receipt"])
        self.assertEqual(result["added"], ["new_probe"])
        self.assertFalse(result["regression_pass"])

    def test_process_monitor_requires_live_pid_and_fresh_heartbeat(self):
        dead = inspect_process(pid=99999999, heartbeat_path=None, max_age_seconds=30)
        self.assertFalse(dead["process_alive"])
        self.assertEqual(dead["state"], "NOT_RUNNING")
        with tempfile.TemporaryDirectory() as td:
            heartbeat = Path(td) / "heartbeat.json"
            heartbeat.write_text(json.dumps({"observed_at_epoch": 1}), encoding="utf-8")
            stale = inspect_process(pid=os.getpid(), heartbeat_path=heartbeat, max_age_seconds=30)
            self.assertTrue(stale["process_alive"])
            self.assertFalse(stale["heartbeat_fresh"])
            self.assertEqual(stale["state"], "STALE_HEARTBEAT")

    def test_loop_guard_penalizes_duplicate_causal_event(self):
        with tempfile.TemporaryDirectory() as td:
            kernel = MotherboardKernel(Path(td))
            first = kernel.observe_tool(
                tool_name="tool-a", action={"kind": "READ"},
                provider_receipt={"id": "r1"}, consequence={"ok": True},
                readback={"verified": True}, causal_id="cause-1",
            )
            second = kernel.observe_tool(
                tool_name="tool-a", action={"kind": "READ"},
                provider_receipt={"id": "r2"}, consequence={"ok": True},
                readback={"verified": True}, causal_id="cause-1",
            )
            self.assertFalse(first["duplicate_causal_event"])
            self.assertTrue(second["duplicate_causal_event"])
            self.assertEqual(second["verification_state"], "COALESCED_DUPLICATE")

    def test_cycle_restores_state_and_reports_open_edges_without_fake_completion(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            kernel = MotherboardKernel(root)
            kernel.set_objective("OBJ-CYCLE", ["edge-open"])
            cycle = kernel.run_cycle(root / "state" / "heartbeat.json")
            self.assertEqual(cycle["loop_state"], "CONTINUE_OPEN_EDGES")
            self.assertEqual(cycle["unfinished_edges"], ["edge-open"])
            self.assertTrue(cycle["monitor"]["process_alive"])
            self.assertTrue(cycle["monitor"]["heartbeat_fresh"])


if __name__ == "__main__":
    unittest.main()