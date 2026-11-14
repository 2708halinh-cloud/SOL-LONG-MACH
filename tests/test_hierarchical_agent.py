"""Bounded, deterministic tests for the user-supplied tree navigator."""
import importlib.util
import pathlib
import unittest

MODULE = pathlib.Path(__file__).resolve().parents[1] / "runtime" / "hierarchical_agent.py"
spec = importlib.util.spec_from_file_location("hierarchical_agent", MODULE)
nav_module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(nav_module)


class NavigatorTests(unittest.TestCase):
    def setUp(self):
        self.n = nav_module.HierarchicalNavigator(nav_module.DEMO_SPACE)

    def test_stepwise_success(self):
        r = self.n.execute_traversal(r"C:\Users\Halin\.config")
        self.assertTrue(r["ok"])
        self.assertEqual(len(r["steps"]), 3)
        self.assertEqual(r["proof_scope"], "SIMULATED_GRAPH_ONLY")

    def test_no_hop_to_non_child(self):
        r = self.n.execute_traversal(r"C:\Halin\.config")
        self.assertFalse(r["ok"])
        self.assertEqual(r["blocked_at"], "C:")

    def test_reject_parent_path_escape(self):
        with self.assertRaises(ValueError):
            self.n.execute_traversal(r"C:\Users\..\Windows")

    def test_reject_unsupplied_projection(self):
        with self.assertRaises(ValueError):
            nav_module.project_six_from_supplied_source(
                {"entity_id": "X", "origin_source": "packet", "projections": {}}
            )

    def test_six_projection_direct_copy(self):
        packet = {"entity_id": "X", "origin_source": "packet",
                  "projections": {k: {"source_assertion": k} for k in nav_module.SIX_KEYS}}
        r = nav_module.project_six_from_supplied_source(packet)
        self.assertEqual(r["projection_count"], 6)
        self.assertFalse(r["inference_applied"])
        self.assertFalse(r["readback_verified"])


if __name__ == "__main__":
    unittest.main()
