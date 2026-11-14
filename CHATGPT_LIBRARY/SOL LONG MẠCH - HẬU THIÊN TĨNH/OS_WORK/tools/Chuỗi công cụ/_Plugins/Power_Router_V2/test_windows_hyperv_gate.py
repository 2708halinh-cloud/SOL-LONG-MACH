"""Windows alias checks: source-only, no host connection or route execution."""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import power_capability_router as router

class WindowsAliasTest(unittest.TestCase):
    def test_assumption_is_not_live_state(self):
        tools = Path(__file__).resolve().parents[3]
        out = router.inspect_windows_hyperv_gate(
            tools, now=datetime(2026, 10, 18, 8, 35, tzinfo=timezone.utc))
        self.assertEqual(out["alias"], "SOL_WIN11_HYPERV_GATE")
        self.assertEqual(out["target_host"], "DESKTOP-86ITNQ4")
        self.assertTrue(out["ndis_lease_expired"])
        self.assertTrue(out["ndis_current_recheck_required"])
        self.assertIsNone(out["hyperv_gateway"])
        self.assertFalse(out["services_verified"])
        self.assertFalse(out["qemu_verified"])
        self.assertFalse(out["action_executed"])

    def test_hyperv_gateway_cannot_be_invented(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / router.WINDOWS_HYPERV_GATE_PROFILE
            path.parent.mkdir(parents=True, exist_ok=True)
            data = json.loads((Path(__file__).parent / "SOL_WIN11_HYPERV_GATE.json").read_text(encoding="utf-8"))
            data["links"][1]["reported_gateway"] = "172.23.0.254"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "GATEWAY_FORBIDDEN"):
                router.inspect_windows_hyperv_gate(root)

if __name__ == "__main__":
    unittest.main()
