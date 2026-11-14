import json
import tempfile
import unittest
from pathlib import Path

from runtime.sol_brain import AgentContinuity, ConversationIngestor, EvidenceStore, InteractionContext, MediaCatalog, infer_affect


class SolBrainTests(unittest.TestCase):
    def test_continuity_does_not_freeze_profile(self):
        memory = AgentContinuity()
        a = memory.observe("I prefer concise answers", source_ref="chat://1")
        b = memory.observe("Today I want a detailed explanation", source_ref="chat://2")
        self.assertNotEqual(a["event_id"], b["event_id"])
        self.assertEqual(memory.current_profile(), {})
        self.assertEqual(len(memory.events()), 2)

    def test_interaction_status_is_not_assumed(self):
        state = InteractionContext().snapshot()
        self.assertEqual(state["status"], "UNSPECIFIED")
        self.assertEqual(state["user_intent"], "NOT_INFERRED")
        self.assertEqual(state["assumptions"], [])

    def test_affect_is_ephemeral_not_identity_or_memory(self):
        result = infer_affect("I NEED THIS NOW")
        self.assertTrue(result["ephemeral"])
        self.assertIsNone(result["personality"])
        self.assertIsNone(result["interaction_status"])
        self.assertFalse(result["persistent_memory_write"])
        self.assertTrue(all(0 <= v <= 1 for v in result["hypotheses"].values()))

    def test_ingestor_preserves_raw_source_and_marks_unknown_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "chat.jsonl"
            p.write_text(json.dumps({"role":"user","content":"hello"}) + "\n" +
                         json.dumps({"speaker":"Sol","text":"hi"}) + "\n", encoding="utf-8")
            rows = list(ConversationIngestor().read_jsonl(p))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["content"], "hello")
            self.assertEqual(rows[1]["normalization_status"], "NORMALIZED")
            self.assertTrue(rows[0]["source_ref"].endswith("chat.jsonl#1"))

    def test_evidence_store_does_not_promote_inference_to_fact(self):
        store = EvidenceStore()
        item = store.append(kind="inference", payload={"affect":"frustration"},
                            source_ref="chat://3", observed_at="2026-11-05T00:00:00Z")
        self.assertEqual(item["evidence_class"], "INFERENCE")
        self.assertFalse(item["verified_fact"])
        self.assertEqual(len(store.items()), 1)

    def test_media_catalog_hashes_original_without_claiming_analysis(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "clip.mp4"
            p.write_bytes(b"video-bytes")
            item = MediaCatalog().catalog(p, source_ref="archive://clip")
            self.assertEqual(item["media_kind"], "video")
            self.assertTrue(item["sha256"])
            self.assertEqual(item["content_analysis"], "NOT_PERFORMED")
            self.assertEqual(item["source_ref"], "archive://clip")


if __name__ == "__main__":
    unittest.main()
