#!/usr/bin/env python3
"""Regression tests for the read-only one-COMPUTER inspector."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "verify_computer_khi_single_root.py"
spec = importlib.util.spec_from_file_location("single_computer", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class SingleComputerTests(unittest.TestCase):
    def test_legacy_is_not_mistaken_for_done(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / mod.P / "SOL_COMPUTER").mkdir(parents=True)
            status = mod.inspect(root)
            self.assertEqual(status["state"], "MIGRATION_PENDING")
            self.assertTrue(status["legacy_path_present"])

    def test_one_root_after_migration(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / mod.P
            home.mkdir(parents=True)
            for name in mod.ROOT_COMPONENTS:
                if name.endswith(".json"):
                    (home / name).write_text("{}", encoding="utf-8")
                else:
                    (home / name).mkdir()
            self.assertEqual(mod.inspect(root)["state"], "CONSOLIDATED")

    def test_absent_components_are_not_done(self):
        with tempfile.TemporaryDirectory() as td:
            status = mod.inspect(Path(td))
            self.assertEqual(status["state"], "INCOMPLETE")
            self.assertIn("CENTER_TAM.json", status["missing_canonical_components"])

if __name__ == "__main__":
    unittest.main()
