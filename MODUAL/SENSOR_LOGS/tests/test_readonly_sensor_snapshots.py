"""Regression checks for sensor snapshot privacy and execution safety.

Runs on a hosted Python runner without Windows, provider credentials, or source
sensor bytes. Live stream behavior still requires exact-target device readback.
"""
from __future__ import annotations

import ast
import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "telemetry_buffer_sync.py"
SYNC_HELPER = ROOT / "source" / "modual_github_sync.py"
STATE = ROOT / "MODUAL_PARAMETER_CURRENT.json"


def rows(name: str) -> list[list[str]]:
    with (ROOT / name).open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


class SensorSnapshotIntegrity(unittest.TestCase):
    def test_bulk_snapshot_is_header_only(self):
        header = rows("BULK_HEADER_CURRENT.csv")
        snapshot = rows("BULK_LATEST_CURRENT.csv")
        self.assertEqual(len(header), 1)
        self.assertEqual(len(header[0]), 408)
        self.assertEqual(snapshot, header)

    def test_live_snapshot_is_header_only(self):
        header = rows("LIVE_HEADER_CURRENT.csv")
        snapshot = rows("LIVE_LATEST_CURRENT.csv")
        self.assertEqual(len(header), 1)
        self.assertEqual(len(header[0]), 358)
        self.assertEqual(snapshot, header)

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

    def test_scheduler_default_is_finite_and_loop_is_explicit(self):
        content = SOURCE.read_text(encoding="utf-8")
        self.assertIn('if args in ([], ["--once"]):', content)
        self.assertIn('elif args == ["--loop"]:', content)
        self.assertIn('Usage: telemetry_buffer_sync.py [--once|--loop]', content)

    def test_sync_helper_does_not_stage_raw_latest_rows(self):
        content = SYNC_HELPER.read_text(encoding="utf-8")
        self.assertNotIn("_last_nonempty_line", content)
        self.assertNotIn("latest_row", content)
        self.assertIn('"live_raw_committed": False', content)
        self.assertIn('"raw_sensor_rows_committed": False', content)
        self.assertIn("for key, value in previous_state.items()", content)
        self.assertIn("if key not in state", content)

    def test_current_state_has_header_only_publication_policy(self):
        state = json.loads(STATE.read_text(encoding="utf-8"))
        policy = state["sync_policy"]
        self.assertNotIn("latest_row", policy["bulk_representation"])
        self.assertFalse(policy["live_raw_committed"])
        self.assertFalse(policy["latest_row_committed"])
        self.assertFalse(state["privacy_policy"]["raw_sensor_rows_committed"])
        self.assertTrue(state.get("session_observations"))
        self.assertTrue(state.get("independent_provider_continuation"))


if __name__ == "__main__":
    unittest.main()
