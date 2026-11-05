import json
import tempfile
import unittest
from pathlib import Path

from runtime.sol_brain import (
    AgentContinuity,
    ConversationIngestor,
    EvidenceStore,
    MediaCatalog,
    RelationshipState,
    infer_affect,
)


class SolBrainTests(unittest.TestCase):
    def test_continuity_does_not_freeze_personality_or_relationship(self):
        continuity = AgentContinuity()
        first = continuity.observe("I prefer concise answers", source_ref="chat://1")
        second = continuity.observe("Today I want a detailed explanation", source_ref="chat://2")
        self.assertNotEqual(first["event_id"], second["event_id"])
        self.assertEqual(continuity.current_profile(), {})
        relation = RelationshipState().snapshot()
        self.assertEqual(relation["label"], "UNSPECIFIED")
        self.assertEqual(relation["affection"], "UNSPECIFIED")
        self.assertFalse(relation["assumes_romance"])
        self.assertFalse(relation["assumes_rejection"])

    def test_affect_is_temporary_hypothesis_not_identity_or_memory(self):
        result = infer_affect("I NEED THIS NOW")
        self.assertIn("hypotheses", result)
        self.assertTrue(result["ephemeral"])
        self.assertNotIn("personality", result)
        self.assertNotIn("relationship", result)
        self.assertTrue(all(0 <= v <= 1 for v in result["hypotheses"].values()))

    def test_ingestor_preserves_raw_source_and_marks_unknown_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "chat.jsonl"
            p.write_text(json.dumps({"role":"user","content":"hello"}) + "\n" +
                         json.dumps({"speaker":"Sol","text":"hi"}) + "\n", encoding="utf-8")
            rows = list(ConversationIngestor().read_jsonl(p))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["content"], "hello")
            self.assertEqual(rows[1]["normalization_status"], "UNKNOWN_SCHEMA")
            self.assertTrue(rows[0]["source_ref"].endswith("chat.jsonl#1"))

    def test_evidence_store_does_not_promote_inference_to_fact(self):
        store = EvidenceStore()
        item = store.append(kind="inference", payload={"affect":"frustration"},
                            source_ref="chat://3", observed_at="2026-11-05T00:00:00Z")
        self.assertEqual(item["evidence_class"], "INFERENCE")
        self.assertFalse(item["verified_fact"])
        self.assertEqual(len(store.items()), 1)

    def test_media_catalog_hashes_original_without_claiming_visual_understanding(self):
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
