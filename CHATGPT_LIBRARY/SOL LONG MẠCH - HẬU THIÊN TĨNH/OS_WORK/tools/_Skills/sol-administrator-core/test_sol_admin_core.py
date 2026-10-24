import sqlite3
import hashlib
import tempfile
import unittest
from pathlib import Path

from sol_admin_core import Administrator, CoreJournal


class AdministratorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.journal = CoreJournal(self.root / "core.sqlite")
        self.admin = Administrator(self.journal)

    def test_probe_hash_and_journal_chain(self):
        source = self.root / "input.txt"
        source.write_text("raw evidence", encoding="utf-8")
        expected = hashlib.sha256(b"raw evidence").hexdigest()
        result = self.admin.probe_file(source, expected)
        self.assertTrue(result.exists)
        self.assertFalse(result.drift)
        self.assertTrue(self.journal.verify_chain())

    def test_drift_is_detected(self):
        source = self.root / "input.txt"
        source.write_text("changed", encoding="utf-8")
        result = self.admin.probe_file(source, "0" * 64)
        self.assertTrue(result.drift)
        decision = self.admin.authorize(
            provenance_ok=True, drift_score=1,
            journal_integrity_ok=True, action="commit"
        )
        self.assertFalse(decision["allowed"])
        self.assertEqual(decision["gate"], "STOP_FORWARD")

    def test_missing_provenance_blocks(self):
        decision = self.admin.authorize(
            provenance_ok=False, drift_score=0,
            journal_integrity_ok=True, action="write"
        )
        self.assertFalse(decision["allowed"])

    def test_corrupt_journal_is_detected(self):
        self.journal.append("TEST", "unit", {"ok": True})
        with sqlite3_connect(self.root / "core.sqlite") as db:
            db.execute("UPDATE journal SET payload_json='{}' WHERE seq=1")
        self.assertFalse(self.journal.verify_chain())


class sqlite3_connect:
    def __init__(self, path):
        import sqlite3
        self.db = sqlite3.connect(path)
    def __enter__(self):
        return self.db
    def __exit__(self, *args):
        self.db.close()


if __name__ == "__main__":
    unittest.main()
