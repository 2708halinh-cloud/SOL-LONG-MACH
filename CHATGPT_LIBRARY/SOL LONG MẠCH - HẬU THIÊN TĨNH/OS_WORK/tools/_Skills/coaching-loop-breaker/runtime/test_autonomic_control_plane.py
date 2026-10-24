import tempfile
import unittest
from pathlib import Path

from autonomic_control_plane import CoreJournal, decide, probe_file, run_cycle


class ControlPlaneTests(unittest.TestCase):
    def test_journal_hash_chain_verifies_after_appends(self):
        with tempfile.TemporaryDirectory() as tmp:
            journal = CoreJournal(Path(tmp) / "core.sqlite")
            journal.append("INPUT", {"source": "test", "sha256": "abc"})
            journal.append("DECISION", {"action": "ALLOW"})
            self.assertEqual(journal.verify_chain()[0], True)

    def test_missing_evidence_holds_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            journal = CoreJournal(Path(tmp) / "core.sqlite")
            result = run_cycle(journal, [Path(tmp) / "missing.toml"])
            self.assertEqual(result.action, "HOLD_AND_DIAGNOSE")
            self.assertTrue(any("PROBE_MISSING" in x for x in result.reasons))

    def test_disk_pressure_triggers_hold(self):
        result = decide([], True, disk_used_percent=90.0)
        self.assertEqual(result.action, "HOLD_AND_DIAGNOSE")
        self.assertIn("DISK_PRESSURE_STOP", result.reasons)

    def test_clean_probe_allows(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "root.toml"
            artifact.write_text("root = 'SOL'\n", encoding="utf-8")
            probe = probe_file(artifact)
            result = decide([probe], True, disk_used_percent=45.0)
            self.assertEqual(probe.status, "OK")
            self.assertEqual(len(probe.sha256), 64)
            self.assertEqual(result.action, "ALLOW")

    def test_endpoint_failure_is_recorded_and_holds(self):
        with tempfile.TemporaryDirectory() as tmp:
            journal = CoreJournal(Path(tmp) / "core.sqlite")
            def broken():
                raise TimeoutError("simulated timeout")
            result = run_cycle(journal, [], endpoint_probes={"/api/state": broken})
            self.assertEqual(result.action, "HOLD_AND_DIAGNOSE")
            self.assertTrue(any("PROBE_ERROR:/api/state" in x for x in result.reasons))
            self.assertEqual(journal.verify_chain()[0], True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
