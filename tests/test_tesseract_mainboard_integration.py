import tempfile
import unittest
from pathlib import Path

from runtime.continuity_guard import Checkpoint, Edge, load_checkpoint
from runtime.motherboard_control_plane import CpuSocket, DiskWriteGuard
from runtime.companion_consequence_gate import SOURCE as CONSEQUENCE_SOURCE
from runtime.tesseract_mainboard import TesseractMotherboard
from runtime.tesseract_snn.core import EnergyCluster, Neuron, SNNEngine


class TesseractMainboardIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.checkpoint_path = root / "checkpoint.json"
        self.journal_path = root / "core-journal.jsonl"
        self.guard = DiskWriteGuard(critical_free_bytes=1)
        self.sockets = [
            CpuSocket("cpu1", "REMOTE_A", "api", True, True, True, True, ("write", "read")),
            CpuSocket("cpu2", "LOCAL", "ollama", True, True, True, True, ("write", "read")),
        ]
        self.calls = []

    def tearDown(self):
        self.temp.cleanup()

    def board(self, executors=None):
        return TesseractMotherboard(
            sockets=self.sockets,
            executors=executors or {},
            checkpoint_path=self.checkpoint_path,
            journal_path=self.journal_path,
            disk_guard=self.guard,
        )

    def edge(self, edge_id="E1", *, carrier_ids=("cpu1",), write=True, capability="write"):
        return Edge(
            edge_id=edge_id,
            target=f"target://{edge_id}",
            callable_now=True,
            candidate_carriers=list(carrier_ids),
            evidence={
                "capability": capability,
                "authorized": True,
                "target_identity_verified": True,
                "policy_allowed": True,
                "destructive_change": False,
                "protected_target": False,
                "explicit_approval": False,
                "write_required": write,
            },
        )

    @staticmethod
    def good_result(edge, carrier):
        return {
            "success": True,
            "action_kind": "WRITE",
            "provider_receipt": {"carrier": carrier, "receipt_id": f"receipt-{edge.edge_id}"},
            "observable_consequence": {"target": edge.target, "changed": True},
            "readback": {"verified": True, "source": edge.target, "sha256": "a" * 64},
            "state_consistent": True,
        }

    def test_open_task_runs_one_edge_but_does_not_close_turn_with_other_work_open(self):
        def execute(socket, edge, carrier):
            self.calls.append((socket.socket_id, edge.edge_id))
            return self.good_result(edge, carrier)

        cp = Checkpoint(
            objective_id="OBJ-OPEN-1",
            source_marker="SOURCE_DIRECT",
            lineage_ref="LINEAGE-1",
            edges=[self.edge("E1"), self.edge("E2", carrier_ids=("cpu2",))],
        )
        out = self.board({"cpu1": execute, "cpu2": execute}).run_cycle(
            cp,
            source_refs=["github://source/commit"],
            history_refs=["sha256:" + "b" * 64],
            disk_sample={"total_bytes": 100, "free_bytes": 20, "sample_fresh": True},
            max_steps=1,
        )
        self.assertEqual(out["state"], "OPEN_CONTINUE")
        self.assertEqual(out["steps"], 1)
        self.assertFalse(out["objective_done"])
        self.assertFalse(out["completion_allowed"])
        self.assertEqual(out["next_edge"], "E2")
        self.assertEqual(len(self.calls), 1)

    def test_failed_provider_route_falls_back_to_another_ready_socket(self):
        def fail(socket, edge, carrier):
            self.calls.append(socket.socket_id)
            return {"success": False, "error": "provider timeout"}

        def succeed(socket, edge, carrier):
            self.calls.append(socket.socket_id)
            return self.good_result(edge, carrier)

        cp = Checkpoint(
            objective_id="OBJ-FAILOVER",
            source_marker="SOURCE_DIRECT",
            lineage_ref="LINEAGE-2",
            edges=[self.edge(carrier_ids=("cpu1", "cpu2"))],
        )
        out = self.board({"cpu1": fail, "cpu2": succeed}).run_cycle(
            cp,
            source_refs=["repo://source"],
            history_refs=["sha256:" + "c" * 64],
            disk_sample={"total_bytes": 100, "free_bytes": 20, "sample_fresh": True},
            max_steps=4,
        )
        self.assertEqual(self.calls, ["cpu1", "cpu2"])
        self.assertEqual(out["state"], "OBJECTIVE_DONE")
        self.assertTrue(out["completion_allowed"])

    def test_gate1_denial_preserves_open_task_and_does_not_call_provider(self):
        def forbidden(socket, edge, carrier):
            self.fail("provider must not be called when target identity is unverified")

        e = self.edge()
        e.evidence["target_identity_verified"] = False
        cp = Checkpoint("OBJ-GATE1", "SOURCE_DIRECT", "LINEAGE-3", edges=[e])
        out = self.board({"cpu1": forbidden}).run_cycle(
            cp,
            source_refs=["repo://source"],
            history_refs=["sha256:" + "d" * 64],
            disk_sample={"total_bytes": 100, "free_bytes": 20, "sample_fresh": True},
            max_steps=4,
        )
        self.assertEqual(out["state"], "OPEN_ROUTE_DISCOVERY_REQUIRED")
        self.assertFalse(out["objective_done"])
        self.assertTrue(cp.edges[0].evidence["carrier_failures"])

    def test_gate2_rejects_success_flag_without_independent_readback(self):
        def false_success(socket, edge, carrier):
            return {
                "success": True,
                "action_kind": "WRITE",
                "provider_receipt": {"id": "receipt"},
                "observable_consequence": {"changed": True},
                "readback": {"verified": False},
                "state_consistent": True,
            }

        cp = Checkpoint("OBJ-GATE2", "SOURCE_DIRECT", "LINEAGE-4", edges=[self.edge()])
        out = self.board({"cpu1": false_success}).run_cycle(
            cp,
            source_refs=["repo://source"],
            history_refs=["sha256:" + "e" * 64],
            disk_sample={"total_bytes": 100, "free_bytes": 20, "sample_fresh": True},
            max_steps=2,
        )
        self.assertEqual(out["state"], "OPEN_ROUTE_DISCOVERY_REQUIRED")
        self.assertFalse(out["objective_done"])
        self.assertFalse(cp.edges[0].grounded_done())

    def test_disk_guard_blocks_nonessential_writes_but_allows_read_only_edges(self):
        def execute(socket, edge, carrier):
            self.calls.append(edge.edge_id)
            return self.good_result(edge, carrier)

        cp = Checkpoint(
            "OBJ-PMIC",
            "SOURCE_DIRECT",
            "LINEAGE-5",
            edges=[
                self.edge("WRITE", carrier_ids=("cpu1",), write=True),
                self.edge("READ", carrier_ids=("cpu2",), write=False, capability="read"),
            ],
        )
        board = self.board({"cpu1": execute, "cpu2": execute})
        out = board.run_cycle(
            cp,
            source_refs=["repo://source"],
            history_refs=["sha256:" + "f" * 64],
            disk_sample={"total_bytes": 100, "free_bytes": 10, "sample_fresh": True},
            max_steps=4,
        )
        self.assertEqual(self.calls, ["READ"])
        self.assertEqual(out["state"], "OPEN_ROUTE_DISCOVERY_REQUIRED")
        self.assertTrue(cp.edges[0].evidence["resource_guard_blocked"])
        self.assertTrue(cp.edges[1].grounded_done())

        # Two consecutive safe samples restore write permission; the third cycle
        # must re-arm the same OPEN edge rather than forgetting it.
        board.run_cycle(cp, source_refs=["repo://source"], history_refs=["sha256:" + "f" * 64],
                        disk_sample={"total_bytes": 100, "free_bytes": 20, "sample_fresh": True})
        out = board.run_cycle(cp, source_refs=["repo://source"], history_refs=["sha256:" + "f" * 64],
                              disk_sample={"total_bytes": 100, "free_bytes": 20, "sample_fresh": True})
        self.assertIn("WRITE", self.calls)
        self.assertTrue(out["objective_done"])

    def test_missing_source_or_history_keeps_task_open_without_action(self):
        def execute(socket, edge, carrier):
            self.fail("no action before source and history anchors exist")

        cp = Checkpoint("OBJ-SOURCE", "SOURCE_DIRECT", "LINEAGE-6", edges=[self.edge()])
        out = self.board({"cpu1": execute}).run_cycle(
            cp,
            source_refs=[],
            history_refs=["sha256:" + "1" * 64],
            disk_sample={"total_bytes": 100, "free_bytes": 20, "sample_fresh": True},
        )
        self.assertEqual(out["state"], "OPEN_SOURCE_REVIEW")
        self.assertFalse(out["objective_done"])
        self.assertIsNotNone(load_checkpoint(self.checkpoint_path))

    def test_snn_event_and_append_only_journal_are_part_of_same_cycle(self):
        engine = SNNEngine(
            [Neuron(threshold=0.5, leak=1.0)],
            [],
            [EnergyCluster(1.0, (0,))],
            energy_per_spike=0.1,
        )
        def execute(socket, edge, carrier):
            return self.good_result(edge, carrier)

        cp = Checkpoint("OBJ-SNN", "SOURCE_DIRECT", "LINEAGE-7", edges=[self.edge()])
        out = TesseractMotherboard(
            sockets=self.sockets,
            executors={"cpu1": execute},
            checkpoint_path=self.checkpoint_path,
            journal_path=self.journal_path,
            disk_guard=self.guard,
            snn_engine=engine,
        ).run_cycle(
            cp,
            source_refs=["repo://source"],
            history_refs=["sha256:" + "2" * 64],
            disk_sample={"total_bytes": 100, "free_bytes": 20, "sample_fresh": True},
        )
        from runtime.tesseract_snn.journal import AppendOnlyJournal
        self.assertTrue(AppendOnlyJournal(self.journal_path).verify())
        self.assertTrue(out["journal_verified"])
        self.assertEqual(out["snn_spikes"], [0])
        self.assertTrue(out["objective_done"])


    def test_companion_gate_verifies_exact_local_target_bytes(self):
        target = Path(self.temp.name) / "target.txt"
        target.write_bytes(b"grounded consequence")
        digest = __import__("hashlib").sha256(target.read_bytes()).hexdigest()
        edge = self.edge()
        edge.evidence["local_file_target"] = True
        edge.evidence["consequence_source_ref"] = CONSEQUENCE_SOURCE

        def execute(socket, edge, carrier):
            result = self.good_result(edge, carrier)
            result.update({
                "action_id": "ACTION-LOCAL-1",
                "target_relpath": "target.txt",
                "consequence_ref": "target://target.txt",
                "receipt_ref": "receipt://provider/1",
            })
            result["readback"]["sha256"] = digest
            return result

        cp = Checkpoint("OBJ-CONSEQUENCE", "SOURCE_DIRECT", "LINEAGE-8", edges=[edge])
        board = TesseractMotherboard(
            sockets=self.sockets,
            executors={"cpu1": execute},
            checkpoint_path=self.checkpoint_path,
            journal_path=self.journal_path,
            disk_guard=self.guard,
            consequence_root=Path(self.temp.name),
        )
        out = board.run_cycle(
            cp,
            source_refs=["repo://source"],
            history_refs=["sha256:" + "3" * 64],
            disk_sample={"total_bytes": 100, "free_bytes": 20, "sample_fresh": True},
        )
        self.assertEqual(out["state"], "OBJECTIVE_DONE")
        self.assertTrue(out["completion_allowed"])

    def test_companion_gate_rejects_mismatched_target_hash(self):
        target = Path(self.temp.name) / "target.txt"
        target.write_bytes(b"actual target bytes")
        edge = self.edge()
        edge.evidence["local_file_target"] = True
        edge.evidence["consequence_source_ref"] = CONSEQUENCE_SOURCE

        def execute(socket, edge, carrier):
            result = self.good_result(edge, carrier)
            result.update({
                "action_id": "ACTION-LOCAL-2",
                "target_relpath": "target.txt",
                "consequence_ref": "target://target.txt",
                "receipt_ref": "receipt://provider/2",
            })
            result["readback"]["sha256"] = "0" * 64
            return result

        cp = Checkpoint("OBJ-CONSEQUENCE-MISMATCH", "SOURCE_DIRECT", "LINEAGE-9", edges=[edge])
        board = TesseractMotherboard(
            sockets=self.sockets,
            executors={"cpu1": execute},
            checkpoint_path=self.checkpoint_path,
            journal_path=self.journal_path,
            disk_guard=self.guard,
            consequence_root=Path(self.temp.name),
        )
        out = board.run_cycle(
            cp,
            source_refs=["repo://source"],
            history_refs=["sha256:" + "4" * 64],
            disk_sample={"total_bytes": 100, "free_bytes": 20, "sample_fresh": True},
        )
        self.assertFalse(out["objective_done"])
        self.assertEqual(out["state"], "OPEN_ROUTE_DISCOVERY_REQUIRED")
        self.assertFalse(cp.edges[0].grounded_done())


if __name__ == "__main__":
    unittest.main()
