import json
import os
import tempfile
import time
import unittest

from runtime.ram_l1_memory import process_signal, write_receipt, read_receipt


def verifier(signal, results):
    return {
        "passed": all(r.status == "success" for r in results),
        "source_present": bool(signal.get("source_id")),
        "branch_count": len(results),
    }


class RamL1Tests(unittest.TestCase):
    def test_parallel_branches_and_verified_commit(self):
        def a(s):
            time.sleep(0.08)
            return {"source": s["source_id"], "finding": "A"}
        def b(s):
            time.sleep(0.08)
            return {"source": s["source_id"], "finding": "B"}

        start = time.monotonic()
        receipt = process_signal(
            {"source_id": "test-001", "signal": "inspect"},
            {"history": a, "dependencies": b},
            max_workers=2, required_branches=["history", "dependencies"],
            verifier=verifier, commit_requested=True,
        )
        elapsed = time.monotonic() - start
        self.assertEqual(receipt.status, "VERIFIED")
        self.assertTrue(receipt.commit_allowed)
        self.assertLess(elapsed, 0.15)
        self.assertEqual(len(receipt.branches), 2)

    def test_failure_blocks_required_branch(self):
        def broken(_):
            raise RuntimeError("synthetic failure")
        receipt = process_signal(
            {"source_id": "test-002"}, {"required": broken},
            required_branches=["required"], verifier=verifier, commit_requested=True
        )
        self.assertEqual(receipt.status, "BLOCKED")
        self.assertFalse(receipt.commit_allowed)

    def test_no_verifier_never_claims_verified(self):
        receipt = process_signal({"signal": "x"}, {"branch": lambda s: {"ok": True}})
        self.assertEqual(receipt.status, "PARTIAL")
        self.assertFalse(receipt.commit_allowed)

    def test_receipt_write_readback(self):
        receipt = process_signal(
            {"source_id": "test-003"}, {"lookup": lambda s: {"found": True}},
            verifier=verifier
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "receipt.json")
            write_receipt(receipt, path)
            loaded = read_receipt(path)
            self.assertEqual(loaded["receipt_id"], receipt.receipt_id)
            self.assertEqual(loaded["signal_sha256"], receipt.signal_sha256)


if __name__ == "__main__":
    unittest.main(verbosity=2)
