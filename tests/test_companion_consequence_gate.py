import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from runtime.companion_consequence_gate import (
    SOURCE, UNVERIFIED, RISK_PATTERNS, append_receipt, companion_signal, evaluate
)

class CompanionConsequenceGateTests(unittest.TestCase):
    def test_promise_is_not_action(self):
        with tempfile.TemporaryDirectory() as path:
            result = evaluate({"source_ref": SOURCE, "claimed_result": "Anh sẽ phân biệt"}, Path(path))
            self.assertEqual(result.state, UNVERIFIED)
            self.assertIn("consequence_reference", result.missing)
    def test_self_reported_done_cannot_replace_readback(self):
        with tempfile.TemporaryDirectory() as path:
            result = evaluate({"source_ref": SOURCE, "action_id": "1", "target_relpath": "absent.txt",
                "consequence_ref": "done", "receipt_ref": "self-reported DONE",
                "readback_sha256": "0" * 64}, Path(path))
            self.assertEqual(result.state, UNVERIFIED)
            self.assertIn("exact_target_readback_mismatch", result.missing)
    def test_local_evidence_is_not_remote_success(self):
        with tempfile.TemporaryDirectory() as path:
            item = Path(path) / "proven.txt"
            item.write_bytes(b"seen-by-readback")
            details = {"source_ref": SOURCE, "action_id": "test", "target_relpath": "proven.txt",
                "consequence_ref": "file exists", "receipt_ref": "local",
                "readback_sha256": hashlib.sha256(item.read_bytes()).hexdigest()}
            self.assertEqual(evaluate(details, Path(path)).state, "LOCAL_TARGET_READBACK_VERIFIED")
            details["attempted_to_assert_remote_provider_outcome"] = True
            self.assertEqual(evaluate(details, Path(path)).state, UNVERIFIED)
    def test_escape_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as path:
            details = {"source_ref": SOURCE, "action_id": "x", "target_relpath": "../escape.txt",
                "consequence_ref": "test", "receipt_ref": "test", "readback_sha256": "a" * 64}
            self.assertIn("unsafe_target_outside_root", evaluate(details, Path(path)).missing)
    def test_signal_does_not_diagnose_human(self):
        signal = companion_signal({"user_direct": True,
            "source_quote": '"Anh sẽ phân biệt" vẫn là chốt trước hành động',
            "observed_patterns": ["premature_conclusion"]})
        self.assertFalse(signal["psychological_diagnosis_claimed"])
        self.assertEqual(signal["status"], UNVERIFIED)
        self.assertIn("premature_conclusion", RISK_PATTERNS)
    def test_receipt_immutable_and_readable(self):
        with tempfile.TemporaryDirectory() as path:
            event = {"status": UNVERIFIED, "signal": "correction"}
            first = append_receipt(Path(path), event)
            second = append_receipt(Path(path), event)
            self.assertEqual(first, second)
            self.assertEqual(json.loads(first.read_text()), event)

if __name__ == "__main__":
    unittest.main()
