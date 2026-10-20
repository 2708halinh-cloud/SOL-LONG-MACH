import json
import tempfile
import unittest
from pathlib import Path
from runtime.sol_x66_cloud_continuity import build, fingerprint, atomic_write, OPEN_JOBS, SCHEMA

class ContinuityTests(unittest.TestCase):
    def test_missing_source_is_not_success(self):
        with tempfile.TemporaryDirectory() as root:
            result = build(Path(root), "2026-10-20T00:00:00Z", "12", "abcdef")
            self.assertEqual(result["schema"], SCHEMA)
            self.assertFalse(result["source_snapshot_complete"])
            self.assertFalse(result["overall_objectives_completed"])
            self.assertTrue(result["STAMP_BETA"]["open_source_gaps"])
            self.assertEqual(len(result["source_observations"]), 10)
    def test_evidence_reads_bytes_and_hashes(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "SOURCE.txt"
            path.write_bytes(b"evidence")
            item = fingerprint(Path(root), "SOURCE.txt")
            self.assertTrue(item["hash_verified"])
            self.assertEqual(item["bytes"], 8)
            self.assertEqual(len(item["sha256"]), 64)
    def test_append_only_receipt_content_roundtrip(self):
        with tempfile.TemporaryDirectory() as root:
            dest = Path(root) / "readback" / "CURRENT.json"
            obj = {"STAMP_OLD": "source", "STAMP_LIVE": "now", "STAMP_BETA": "open"}
            atomic_write(dest, obj)
            self.assertEqual(json.loads(dest.read_text()), obj)
    def test_open_objectives_not_closed_by_schedule(self):
        self.assertIn("TESSERACT_6D_WEB_PUBLICATION", OPEN_JOBS)
        self.assertIn("TIME_STONE_MISSING_MESSAGE_PROVENANCE", OPEN_JOBS)

if __name__ == "__main__":
    unittest.main()
