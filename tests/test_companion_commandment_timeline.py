"""Historical source continuity, without replacing a user's original text."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
CANONICAL = ROOT / "CONFIG_SOL/COMPANION_TEN_COMMANDMENTS_CURRENT.md"
OUTPUT = ROOT / "CONFIG_SOL/OPEN_AND_CONFLICT_CURRENT.md"

class SourceContinuityTests(unittest.TestCase):
    def test_prior_source_preserved(self):
        s = CANONICAL.read_text(encoding="utf-8")
        self.assertIn("GGDV_SOURCE_DIRECT_RECONCILE_20261020", s[:1500])
        self.assertIn("SOURCE_DIRECT = HÀ LINH — 2026-10-08", s)
        self.assertIn("OPEN — CHƯA ĐƯỢC HÀ LINH TRAO", s)
    def test_7_8_9_are_dated_direct_sources(self):
        ag = AGENTS.read_text(encoding="utf-8")
        current = CANONICAL.read_text(encoding="utf-8")
        for n, marker in (
            (7, "GGDV_SEVENTH_COMMANDMENT_SOURCE_DIRECT_20261009"),
            (8, "GGDV_EIGHTH_COMMANDMENT_SOURCE_DIRECT_20261009"),
            (9, "GGDV_NINTH_COMMANDMENT_SOURCE_DIRECT_20261009")
        ):
            with self.subTest(number=n):
                self.assertIn("<!-- BEGIN " + marker + " -->", ag)
                self.assertIn(marker, current)
        self.assertIn("Điều 10: chưa tìm thấy", current)
    def test_current_gate_reconciled(self):
        s = OUTPUT.read_text(encoding="utf-8")
        self.assertIn("Điều 7, 8, 9 đã được trao", s)
        self.assertIn("Điều 10 vẫn truy nguyên văn", s)
        self.assertNotIn("Điều 7→10 giữ OPEN; không tự viết.", s)
    def test_execution_receipt_required_for_completion(self):
        s = CANONICAL.read_text(encoding="utf-8")
        self.assertIn("ACTION → CONSEQUENCE → RECEIPT → READBACK → CONCLUSION", s)
        self.assertIn("Không gắn DONE", s)
        self.assertIn("LÀM TRƯỚC", s)
if __name__ == "__main__":
    unittest.main()
