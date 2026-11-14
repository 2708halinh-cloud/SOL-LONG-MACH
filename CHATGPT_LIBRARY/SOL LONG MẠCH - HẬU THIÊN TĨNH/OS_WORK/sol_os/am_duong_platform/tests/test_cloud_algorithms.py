"""SOL Cloud Lab synthetic regression; uses only temp scratch SQLite nodes."""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cloud_algorithms import ReplicaLab, QuorumUnavailable, map_reduce_count, rendezvous


class CloudLabEvals(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.lab = ReplicaLab(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_01_map_reduce_partition_consistency(self):
        items = ["sol","time","sol","space","time","sol"]
        expected = {"sol":3,"space":1,"time":2}
        for w in (1,2,3,5,8):
            self.assertEqual(map_reduce_count(items,w), expected)

    def test_02_map_reduce_empty(self):
        self.assertEqual(map_reduce_count([]),{})

    def test_03_map_reduce_input_bound(self):
        with self.assertRaises(ValueError):
            map_reduce_count(["a"]*10001)

    def test_04_shard_deterministic(self):
        x=rendezvous("memory:event001",("A","B","C"))
        self.assertEqual(x,rendezvous("memory:event001",("A","B","C")))
        self.assertEqual(sorted(x),["A","B","C"])

    def test_05_three_node_quorum(self):
        r=self.lab.put("event-1","v1")
        self.assertEqual(r["acks"],3)
        self.assertEqual(self.lab.get("event-1")["content"],"v1")

    def test_06_one_node_offline_still_reads_and_writes(self):
        self.lab.put("event-1","v1")
        self.lab.set_online("node_c",False)
        r=self.lab.put("event-1","v2")
        self.assertEqual(r["acks"],2)
        self.assertEqual(self.lab.get("event-1")["content"],"v2")

    def test_07_two_nodes_offline_refuses_write(self):
        self.lab.set_online("node_b",False)
        self.lab.set_online("node_c",False)
        with self.assertRaises(QuorumUnavailable):
            self.lab.put("event-2","should not commit")

    def test_08_two_nodes_offline_refuses_read(self):
        self.lab.put("event-1","v1")
        self.lab.set_online("node_a",False)
        self.lab.set_online("node_b",False)
        with self.assertRaises(QuorumUnavailable):
            self.lab.get("event-1")

    def test_09_recovers_stale_replica_after_rejoin(self):
        self.lab.put("event-1","v1")
        self.lab.set_online("node_c",False)
        self.lab.put("event-1","v2")
        self.lab.set_online("node_c",True)
        r=self.lab.repair("event-1")
        self.assertEqual(r["repaired"],1)
        with self.lab._connect("node_c") as db:
            row=db.execute("SELECT content FROM kv WHERE key=?",("event-1",)).fetchone()
        self.assertEqual(row[0],"v2")

    def test_10_anti_corruption_hash_and_repair(self):
        self.lab.put("event-1","v1")
        with self.lab._connect("node_c") as db:
            db.execute("UPDATE kv SET content='corrupted' WHERE key='event-1'")
        self.assertEqual(self.lab.get("event-1")["content"],"v1")
        r=self.lab.repair("event-1")
        self.assertEqual(r["repaired"],1)
        with self.lab._connect("node_c") as db:
            self.assertEqual(db.execute("SELECT content FROM kv WHERE key=?",("event-1",)).fetchone()[0],"v1")

    def test_11_missing_data_not_invented(self):
        self.assertFalse(self.lab.get("unknown")["found"])
        self.assertEqual(self.lab.repair("unknown")["repaired"],0)

    def test_12_restart_reads_sqlite(self):
        original=self.lab.put("event-1","persistent")
        resumed=ReplicaLab(Path(self.tmp.name))
        self.assertEqual(resumed.get("event-1")["content"],"persistent")
        self.assertGreater(resumed.put("event-1","next")["revision"],original["revision"])

    def test_13_invalid_node_denied(self):
        with self.assertRaises(ValueError):
            self.lab.set_online("remote-cloud-node",True)

    def test_14_simulation_not_network(self):
        self.assertTrue(self.lab.put("event-1","v1")["simulation"])

    def test_15_no_false_consensus_claims(self):
        self.assertNotIn("consensus",self.lab.put("event-1","v1"))
        self.assertNotIn("provider_receipt",self.lab.get("event-1"))

    def test_16_no_change_on_quorum_failure(self):
        self.lab.put("event-1","v1")
        self.lab.set_online("node_b",False)
        self.lab.set_online("node_c",False)
        with self.assertRaises(QuorumUnavailable):
            self.lab.put("event-1","v2")
        self.lab.set_online("node_b",True)
        self.lab.set_online("node_c",True)
        self.assertEqual(self.lab.get("event-1")["content"],"v1")

if __name__=="__main__":
    unittest.main()
