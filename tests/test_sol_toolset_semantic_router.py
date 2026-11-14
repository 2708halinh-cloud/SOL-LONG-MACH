"""Semantic translation: don't confuse source tool names with installed capabilities."""
import unittest
from pathlib import Path
from runtime.sol_toolset_semantic_router import load_registry, recommend

REPO = Path(__file__).resolve().parents[1]


class NineFamiliesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load_registry(REPO)

    def test_exactly_nine_transferable_families(self):
        self.assertEqual(len(self.registry["families"]), 9)
        self.assertEqual(self.registry["source"]["raw_action_routes"], 97)
        self.assertTrue(self.registry["policy"]["do_not_mirror_all_97_as_live_tools"])

    def test_work_iterations_translate_to_time_capacity(self):
        out = recommend("Xem chu kỳ iteration và capacity cho dự án", self.registry)
        self.assertEqual(out["candidates"][0]["id"], "TIME_AND_CAPACITY")
        self.assertFalse(out["action_executed"])

    def test_pr_does_not_imply_azure_connection(self):
        out = recommend("Tìm trạng thái PR và commit trong repo", self.registry)
        self.assertEqual(out["candidates"][0]["id"], "CARRIER_GRAPH")
        self.assertFalse(out["azure_connected_inferred"])

    def test_reentry_memory(self):
        out = recommend("Hồi quy ký ức và chỉ dẫn dự án", self.registry)
        self.assertTrue(any(x["id"] == "LIVING_MEMORY" for x in out["candidates"]))

    def test_unknown_task_falls_back_to_probe_not_wait(self):
        out = recommend("nhận tín hiệu hoàn toàn mới chưa gọi tên", self.registry)
        self.assertEqual(out["candidates"][0]["id"], "PROACTIVE_PROBE")
        self.assertEqual(out["next"], "DISCOVER_CALLABLE_PROVIDERS_AND_LOCK_REFERENT")

    def test_user_described_intent_cannot_authorize(self):
        out = recommend("Cập nhật pipeline", self.registry, provider_evidence=[
            {"provider": "GitHub", "source_ref": "repo/example", "observed_at": "2026-10-16"}])
        self.assertFalse(out["authorization_inferred"])
        self.assertFalse(out["action_executed"])
        self.assertTrue(out["raw_toolset_is_not_ground_truth"])

    def test_provider_evidence_needs_provenance(self):
        with self.assertRaises(ValueError):
            recommend("truy dấu", self.registry, provider_evidence=[{"provider": "GitHub"}])


if __name__ == "__main__":
    unittest.main()
