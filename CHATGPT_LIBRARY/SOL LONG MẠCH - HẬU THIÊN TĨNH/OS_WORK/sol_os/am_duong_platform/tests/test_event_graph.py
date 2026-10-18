"""Synthetic regression checks for additive event graph; no personal source bytes."""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import Workrooms

class GraphEvals(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dbpath = Path(self.tmp.name) / "workroom.sqlite3"
        self.db = Workrooms(self.dbpath)
        self.nodes = [self.db.add("sol-main", "test", "DUONG_PHAP_SU",
                                  "source", "Synthetic event " + n,
                                  source_ref="test-only:" + n)["id"]
                      for n in ("A", "B", "C", "D")]
        self.a, self.b, self.c, self.d = self.nodes

    def tearDown(self):
        self.tmp.cleanup()

    def link(self, src, dst, rel="REFERS_TO", evidence="test-only:edge"):
        return self.db.link_events(src, dst, rel, evidence)

    def test_01_requires_real_endpoints(self):
        with self.assertRaisesRegex(ValueError, "EDGE_ENDPOINT_NOT_PERSISTED"):
            self.link(self.a, "ev_" + "f"*32)

    def test_02_requires_evidence_pointer(self):
        with self.assertRaises(ValueError):
            self.link(self.a, self.b, evidence="")

    def test_03_rejects_self_link(self):
        with self.assertRaisesRegex(ValueError, "SELF_EDGE_REFUSED"):
            self.link(self.a, self.a)

    def test_04_relation_allowlist(self):
        with self.assertRaisesRegex(ValueError, "RELATION_NOT_SUPPORTED"):
            self.link(self.a, self.b, "MADE_UP_RELATION")

    def test_05_finds_direct_link(self):
        self.link(self.a, self.b, evidence="test-only:source")
        r = self.db.shortest_connection(self.a, self.b)
        self.assertEqual(r["node_ids"], [self.a, self.b])
        self.assertTrue(r["connected"])
        self.assertEqual(r["edges"][0]["evidence_ref"], "test-only:source")

    def test_06_reverse_traversal_not_reverse_claim(self):
        self.link(self.a, self.b, "DERIVED_FROM")
        r = self.db.shortest_connection(self.b, self.a)
        self.assertEqual(r["edges"][0]["traversal"], "REVERSE")
        self.assertEqual(r["edges"][0]["source_event_id"], self.a)

    def test_07_bfs_shortest_not_first_route(self):
        self.link(self.a, self.b)
        self.link(self.b, self.c)
        self.link(self.c, self.d)
        self.link(self.a, self.d, "SAME_SOURCE")
        r = self.db.shortest_connection(self.a, self.d)
        self.assertEqual(len(r["edges"]), 1)

    def test_08_time_cycle_prevention(self):
        self.link(self.a, self.b, "PRECEDES")
        self.link(self.b, self.c, "PRECEDES")
        with self.assertRaisesRegex(ValueError, "TIME_CYCLE_DETECTED"):
            self.link(self.c, self.a, "PRECEDES")

    def test_09_idempotent_duplicate(self):
        self.assertTrue(self.link(self.a, self.b)["created"])
        self.assertFalse(self.link(self.a, self.b)["created"])

    def test_10_missing_path_not_invented(self):
        r = self.db.shortest_connection(self.a, self.d)
        self.assertFalse(r["connected"])
        self.assertEqual(r["edges"], [])

    def test_11_depth_limit(self):
        self.link(self.a, self.b)
        self.link(self.b, self.c)
        self.assertFalse(self.db.shortest_connection(self.a, self.c, max_depth=1)["connected"])
        self.assertTrue(self.db.shortest_connection(self.a, self.c, max_depth=2)["connected"])

    def test_12_node_budget(self):
        self.link(self.a, self.b)
        r = self.db.shortest_connection(self.a, self.d, max_nodes=1)
        self.assertFalse(r["connected"])
        self.assertEqual(r["status"], "NODE_BUDGET_REACHED")

    def test_13_survives_sqlite_reopen(self):
        self.link(self.a, self.b)
        again = Workrooms(self.dbpath)
        self.assertTrue(again.shortest_connection(self.a, self.b)["connected"])

    def test_14_retains_source_events(self):
        before = len(self.db.events("sol-main"))
        self.link(self.a, self.b)
        self.assertEqual(len(self.db.events("sol-main")), before)

    def test_15_enforces_sqlite_foreign_keys(self):
        with self.db._connect() as conn:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO event_links VALUES(?,?,?,?,?)",
                    ("ev_" + "f"*32, self.a, "REFERS_TO", "test", "2026-10-18")
                )

    def test_16_rejects_unbounded_query(self):
        with self.assertRaisesRegex(ValueError, "DEPTH_BOUND_INVALID"):
            self.db.shortest_connection(self.a, self.b, max_depth=100)
        with self.assertRaisesRegex(ValueError, "NODE_BOUND_INVALID"):
            self.db.shortest_connection(self.a, self.b, max_nodes=0)

if __name__ == "__main__":
    unittest.main()
