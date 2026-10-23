"""Check evidence-first selection without touching user files."""
import importlib.util
import os
import tempfile
import time
import unittest
from unittest.mock import patch
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


    def test_explicit_source_file_override_beats_newer_csv(self):
        with tempfile.TemporaryDirectory() as temp:
            pinned = Path(temp) / "pinned.csv"
            newer = Path(temp) / "newer.csv"
            pinned.write_text("Date,Time,Sensor\\n2026-10-23,15:00,pinned\\n", encoding="utf-8")
            newer.write_text("Date,Time,Sensor\\n2026-10-23,15:00,newer\\n", encoding="utf-8")
            future = time.time() + 120
            os.utime(newer, (future, future))
            with patch.dict(os.environ, {
                "SOL_SENSOR_SOURCE_FILE": str(pinned),
                "SOL_SENSOR_SOURCE_ROOT": str(newer),
            }):
                result = resolver.inspect_sources()
            self.assertTrue(result["source_verified"])
            self.assertEqual(Path(result["selected_source"]), pinned)
            self.assertEqual(Path(result["selected_evidence"]["file"]), pinned)
            self.assertEqual(result["source_override_mode"], "EXACT_FILE")

    def test_missing_explicit_source_does_not_fall_back(self):
        with tempfile.TemporaryDirectory() as temp:
            missing = Path(temp) / "missing.csv"
            fallback = Path(temp) / "fallback.csv"
            fallback.write_text("Date,Time,Sensor\\n2026-10-23,15:00,fallback\\n", encoding="utf-8")
            with patch.dict(os.environ, {
                "SOL_SENSOR_SOURCE_FILE": str(missing),
                "SOL_SENSOR_SOURCE_ROOT": str(fallback),
            }):
                result = resolver.inspect_sources()
            self.assertFalse(result["source_verified"])
            self.assertEqual(result["source_override_mode"], "EXACT_FILE")
            self.assertEqual(len(result["checked"]), 1)
            self.assertEqual(result["checked"][0]["path"], str(missing))

if __name__ == "__main__":
    unittest.main()
