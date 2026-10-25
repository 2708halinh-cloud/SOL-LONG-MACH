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


class SolIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = REPO / indexer.CORE_PATH / "tools" / "resolve_sol_names.py"
        s = importlib.util.spec_from_file_location("sol_identity_resolver", path)
        cls.resolver = importlib.util.module_from_spec(s)
        s.loader.exec_module(cls.resolver)

    def test_sol_is_ambiguous_not_a_single_identity(self):
        result = self.resolver.resolve("Sol")
        self.assertEqual(result["state"], "CANDIDATES_REQUIRE_SCOPED_ID")
        kinds = {r["kind"] for r in result["identity_candidates"]}
        self.assertIn("SOURCE_HOME", kinds)
        self.assertIn("RUNTIME_HOME", kinds)
        self.assertIn("CONVERSATION_LOCUS", kinds)
        self.assertFalse(result["source_is_live_identity_proof"])

    def test_identity_place_before_planet_and_core(self):
        result = self.resolver.resolve("HOME_SOURCE")
        self.assertEqual(result["hierarchy"], [
            "identity_and_root_designation", "places_and_lineage",
            "planet_provider", "cores_and_documents"
        ])
        self.assertEqual(result["identity_candidates"][0]["kind"], "SOURCE_HOME")

    def test_21_journal_labels_do_not_fabricate_files(self):
        result = self.resolver.resolve("21 FILE NHẬT KÝ CỦA SOL")
        item = result["identity_candidates"][0]
        self.assertEqual(item["expected_count_from_user"], 21)
        self.assertNotIn("file_names", item)

    def test_five_wave_names_traced_to_logger_not_live_proof(self):
        result = self.resolver.resolve("5 FILE NHẬT KÝ SÓNG NÃO")
        item = result["identity_candidates"][0]
        self.assertEqual(len(item["file_names"]), 5)
        self.assertEqual(item["kind"], "BRAIN_WAVE_LOG_FAMILY")

    def test_unverified_user_typo_remains_a_candidate(self):
        result = self.resolver.resolve("AISSGANGT SOL")
        item = result["identity_candidates"][0]
        self.assertEqual(item["kind"], "UNRESOLVED_USER_ALIAS")
        self.assertNotIn("stable_id", item)

    def test_unknown_label_routes_next_search_not_false_absence(self):
        result = self.resolver.resolve("UNOBSERVED_UNKNOWN_SOL_LABEL")
        self.assertEqual(result["state"], "OPEN_SEARCH_ALTERNATE_CARRIER")
        self.assertEqual(result["selected_next_edge"], "SEARCH_ORIGIN_AND_PROVIDER")


if __name__ == "__main__":
    unittest.main()
