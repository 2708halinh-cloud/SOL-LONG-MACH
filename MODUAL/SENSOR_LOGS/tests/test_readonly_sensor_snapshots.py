"""Regression checks for the existing sensor snapshot carriers.

Runs without Windows and never edits source data. Live logging and exact
physical paths still require observing the actual connected device.
"""
from __future__ import annotations
import ast
import csv
import io
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "telemetry_buffer_sync.py"

def rows(name: str) -> list[list[str]]:
    with (ROOT / name).open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))

class SensorSnapshotIntegrity(unittest.TestCase):
    def test_bulk_header_and_row_width(self):
        header = rows("BULK_HEADER_CURRENT.csv")[0]
        snapshot = rows("BULK_LATEST_CURRENT.csv")
        self.assertEqual(len(header), 408)
        self.assertEqual(len(snapshot), 2)
        self.assertEqual(snapshot[0], header)
        self.assertEqual(len(snapshot[1]), len(header))

    def test_live_header_and_row_width(self):
        header = rows("LIVE_HEADER_CURRENT.csv")[0]
        snapshot = rows("LIVE_LATEST_CURRENT.csv")
        self.assertEqual(len(header), 358)
        self.assertEqual(len(snapshot), 2)
        self.assertEqual(snapshot[0], header)
        self.assertEqual(len(snapshot[1]), len(header))

    def test_source_reader_never_appends_synthetic_sensor_rows(self):
        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        functions = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        tick = next(n for n in functions if n.name == "record_telemetry_tick")
        code = ast.get_source_segment(source, tick)
        self.assertIsNotNone(code)
        self.assertNotIn('open(BUFFER_CSV, "a"', code)
        self.assertNotIn('["0.0"]', code)
        self.assertIn("source_file_written", code)
        self.assertIn("synthetic_rows_added", code)

    def test_exports_require_separate_enable_flags(self):
        content = SOURCE.read_text(encoding="utf-8")
        self.assertIn("SOL_ENABLE_SENSOR_CLOUD_EXPORT", content)
        self.assertIn("SOL_ENABLE_SENSOR_GITHUB_PUSH", content)

if __name__ == "__main__":
    unittest.main()
