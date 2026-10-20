"""Check evidence-first selection without touching user files."""
import importlib.util
import tempfile
import time
import unittest
from pathlib import Path

module_file = Path(__file__).resolve().parents[1] / "source" / "sensor_root_resolver.py"
spec = importlib.util.spec_from_file_location("sensor_root_resolver", module_file)
resolver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resolver)

class DiscoveryTests(unittest.TestCase):
    def test_real_csv_354_columns(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "HWiNFO_WINDOWS.CSV"
            header = ["Date", "Time", "CPU [MHz]", "GPU [MHz]"] + ["Core %d [MHz]" % n for n in range(350)]
            values = ["20.10.2026", "22:30", "3600", "1200"] + ["500"] * 350
            file.write_text(",".join(header) + "\n" + ",".join(values) + "\n", encoding="utf-8")
            result = resolver.inspect_sources([file])
            self.assertTrue(result["source_verified"])
            self.assertEqual(result["selected_evidence"]["column_count"], 354)
            self.assertFalse(result["live_stream_confirmed"])

    def test_no_fake_source(self):
        with tempfile.TemporaryDirectory() as temp:
            ghost = Path(temp) / "D_legacy"
            result = resolver.inspect_sources([ghost])
            self.assertFalse(result["source_verified"])
            self.assertFalse(ghost.exists())

if __name__ == "__main__":
    unittest.main()
