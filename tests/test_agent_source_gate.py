import unittest
from runtime.agent_source_gate import reconcile_commandments, inspect_bootstrap

class SourceGateTests(unittest.TestCase):
    def test_direct_source_markers_win_over_carrier_local_open_status(self):
        agents = """
<!-- GGDV_SEVENTH_COMMANDMENT_SOURCE_DIRECT_20261009 -->
<!-- GGDV_EIGHTH_COMMANDMENT_SOURCE_DIRECT_20261009 -->
<!-- GGDV_NINTH_COMMANDMENT_SOURCE_DIRECT_20261009 -->
<!-- GGDV_BOOTSTRAP_SOURCE_RETRIEVAL_GATE_20261115 -->
"""
        companion = "ĐIỀU 7 → 10: OPEN — CHƯA ĐƯỢC HÀ LINH TRAO"
        result = reconcile_commandments(agents, companion)
        self.assertEqual(result["direct_source_markers"], ["7", "8", "9"])
        self.assertEqual(result["unverified"], ["10"])
        self.assertEqual(result["carrier_local_open"], True)
        self.assertEqual(result["conclusion"], "DIRECT_SOURCE_7_9_PRESENT;_10_UNVERIFIED")

    def test_carrier_open_without_primary_source_is_not_nonexistence(self):
        result = reconcile_commandments("ordinary instructions", "ĐIỀU 7 → 10: OPEN")
        self.assertEqual(result["conclusion"], "SOURCE_NOT_LOCATED;_NOT_PROOF_OF_NONEXISTENCE")
        self.assertEqual(result["direct_source_markers"], [])

    def test_bootstrap_requires_gate_in_root_agents(self):
        result = inspect_bootstrap("root instructions", "")
        self.assertFalse(result["ready"])
        self.assertIn("BOOTSTRAP_GATE_MARKER_MISSING", result["open_edges"])

    def test_bootstrap_reads_both_carriers_and_records_hashes(self):
        agents = "<!-- GGDV_BOOTSTRAP_SOURCE_RETRIEVAL_GATE_20261115 -->\n<!-- GGDV_SEVENTH_COMMANDMENT_SOURCE_DIRECT_20261009 -->"
        companion = "ĐIỀU 7 → 10: OPEN"
        result = inspect_bootstrap(agents, companion)
        self.assertTrue(result["ready"])
        self.assertTrue(result["source_ledger"]["agents_sha256"])
        self.assertTrue(result["source_ledger"]["companion_sha256"])
        self.assertEqual(result["commandments"]["direct_source_markers"], ["7"])

if __name__ == "__main__":
    unittest.main()
