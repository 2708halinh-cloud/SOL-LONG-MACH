"""Real INDEX must see actual checkout changes and never read secret/symlink bytes."""
from __future__ import annotations

import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / (
    "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/"
    "COMPUTER_KHÍ💜BRAIN_OS_POWER/CORE_PLACES_INDEX_MÁU_🔴_HỎA_REALITY/indexer.py"
)
spec = importlib.util.spec_from_file_location("reality_indexer", SOURCE)
indexer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(indexer)


class RealityIndexTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.repo = Path(temp.name)
        self.root = self.repo / indexer.CORE_PATH
        self.root.mkdir(parents=True)
        for name in indexer.REQUIRED_ENTRIES:
            entry = self.root / name
            if name in ("PUPPETEER_RUNTIME", "CHƯƠNG II — THÂN VẬT LÝ"):
                entry.mkdir()
            else:
                entry.write_text("observed:" + name, encoding="utf-8")

    def test_observed_tree_with_required_paths(self):
        state = indexer.inventory(self.repo, observed_at="2026-10-16T00:00:00Z")
        self.assertTrue(state["index_operational"])
        self.assertEqual(state["required_missing"], [])
        self.assertEqual(state["file_count"], 4)
        self.assertEqual(state["directory_count"], 2)
        self.assertEqual(state["source"], "LOCAL_CHECKOUT_ONLY_NOT_NATIVE_LIBRARY_OR_LIVE_PROVIDER")

    def test_changed_file_bytes_change_digest(self):
        p = self.root / "README.md"
        before = indexer.inventory(self.repo)
        first = next(v for v in before["records"] if v["local_path"] == "README.md")
        p.write_text("different-contents", encoding="utf-8")
        after = indexer.inventory(self.repo)
        second = next(v for v in after["records"] if v["local_path"] == "README.md")
        self.assertNotEqual(first["sha256"], second["sha256"])
        self.assertEqual(second["sha256"], hashlib.sha256(b"different-contents").hexdigest())

    def test_missing_target_changes_next_action(self):
        (self.root / "AGENTS.md").unlink()
        v = indexer.inventory(self.repo)
        self.assertIn("AGENTS.md", v["required_missing"])
        self.assertFalse(v["index_operational"])
        self.assertEqual(v["next_action"], "INSPECT_MISSING_INDEX_SOURCE")

    def test_private_names_and_symlinks_not_followed(self):
        (self.root / "token.json").write_text("SECRET", encoding="utf-8")
        (self.root / ".env").write_text("SECRET", encoding="utf-8")
        outside = self.repo / "outside.txt"
        outside.write_text("NEVER_SCAN", encoding="utf-8")
        try:
            (self.root / "outside-link").symlink_to(outside)
        except (OSError, NotImplementedError):
            pass
        state = indexer.inventory(self.repo)
        names = [v["local_path"] for v in state["records"]]
        self.assertNotIn("token.json", names)
        self.assertNotIn(".env", names)
        self.assertNotIn("outside-link", names)
        self.assertGreaterEqual(state["excluded_entries"], 2)

    def test_markdown_contains_provenance_not_runtime_claim(self):
        result = indexer.inventory(self.repo, observed_at="2026-10-16T00:00:00Z")
        out = indexer.markdown(result)
        self.assertIn("LOCAL_CHECKOUT_ONLY_NOT_NATIVE_LIBRARY_OR_LIVE_PROVIDER", out)
        self.assertIn("PUPPETEER_RUNTIME", out)
        self.assertIn("AGENTS.md", out)

    def test_reject_missing_scope(self):
        (self.root / "README.md").unlink()
        # Index still exists, but its canonical materialization is incomplete.
        self.assertFalse(indexer.inventory(self.repo)["index_operational"])
        import shutil
        shutil.rmtree(self.root)
        with self.assertRaises(ValueError):
            indexer.inventory(self.repo)


if __name__ == "__main__":
    unittest.main()
