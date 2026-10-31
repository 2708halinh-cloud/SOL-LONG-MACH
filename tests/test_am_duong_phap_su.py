import unittest

from runtime.am_duong_phap_su import (
    ActionEvidence, AmDuongPhapSu, Neuron, Tran,
)


class AmDuongPhapSuTests(unittest.TestCase):
    def setUp(self):
        self.engine = AmDuongPhapSu(threshold=0.25)

    def plan(self, run_id, neuron, **yin):
        return (
            Tran(run_id, "tra cứu tri thức")
            .ÂM(source_ref="repo://source", author="HÀ LINH", platform="test",
                authorized=yin.get("authorized", True),
                target_verified=yin.get("target_verified", True))
            .TÂM(policy_allowed=yin.get("policy_allowed", True),
                 quota_available=yin.get("quota_available", True),
                 explicit_approval=yin.get("explicit_approval", False))
            .DƯƠNG(neuron)
        )

    def test_gate1_rejects_unverified_target_before_neuron_runs(self):
        calls = []
        neuron = Neuron("lookup", "tra cứu tri thức",
                        lambda _: calls.append(1) or ActionEvidence({}, True, True, True, True))
        result = self.engine.khai_trận(self.plan("g1", neuron, target_verified=False))
        self.assertEqual(result.status, "GATE1_REJECTED")
        self.assertEqual(calls, [])

    def test_old_stamp_requires_gate2_independent_readback(self):
        neuron = Neuron("lookup", "tra cứu tri thức",
                        lambda _: ActionEvidence({"rows": 2}, True, True, True, True))
        result = self.engine.khai_trận(self.plan("g2", neuron))
        self.assertEqual(result.status, "COMPLETED")
        self.assertEqual([stamp.kind for stamp in result.stamps],
                         ["STAMP_LIVE", "STAMP_OLD"])

    def test_missing_readback_never_becomes_old_or_done(self):
        neuron = Neuron("lookup", "tra cứu tri thức",
                        lambda _: ActionEvidence({"rows": 2}, True, True, False, True))
        result = self.engine.khai_trận(self.plan("no-readback", neuron))
        self.assertEqual(result.status, "READBACK_REJECTED")
        self.assertEqual([stamp.kind for stamp in result.stamps], ["STAMP_LIVE"])

    def test_side_effect_requires_explicit_approval(self):
        calls = []
        neuron = Neuron("email", "tra cứu tri thức gửi email",
                        lambda _: calls.append(1) or ActionEvidence({}, True, True, True, True),
                        side_effect=True)
        result = self.engine.khai_trận(self.plan("side-effect", neuron))
        self.assertEqual(result.status, "GATE1_REJECTED")
        self.assertIn("EXPLICIT_APPROVAL_REQUIRED", result.gate_reasons)
        self.assertEqual(calls, [])

    def test_approved_side_effect_still_requires_readback(self):
        neuron = Neuron("email", "tra cứu tri thức gửi email",
                        lambda _: ActionEvidence({"sent": True}, True, True, True, True),
                        side_effect=True)
        result = self.engine.khai_trận(
            self.plan("approved-side-effect", neuron, explicit_approval=True))
        self.assertEqual(result.status, "COMPLETED")
        self.assertEqual(result.stamps[-1].kind, "STAMP_OLD")

    def test_beta_hypothesis_is_separate_from_live_and_old(self):
        plan = (Tran("beta", "dự kiến triển khai")
                .ÂM(source_ref="repo://source", authorized=True, target_verified=True)
                .TÂM(policy_allowed=True, quota_available=True)
                .GIẢ_THUYẾT("có thể triển khai tuần tới"))
        result = self.engine.khai_trận(plan)
        self.assertEqual(result.status, "NO_NEURON_MATCH")
        self.assertEqual([stamp.kind for stamp in result.stamps],
                         ["STAMP_LIVE", "STAMP_BETA"])

    def test_duplicate_neuron_names_are_rejected(self):
        neuron = Neuron("lookup", "tra cứu tri thức",
                        lambda _: ActionEvidence({}, True, True, True, True))
        self.engine.register(neuron)
        with self.assertRaises(ValueError):
            self.engine.register(neuron)

    def test_duplicate_run_id_is_rejected(self):
        neuron = Neuron("lookup", "tra cứu tri thức",
                        lambda _: ActionEvidence({}, True, True, True, True))
        plan = self.plan("duplicate", neuron)
        self.engine.khai_trận(plan)
        with self.assertRaises(ValueError):
            self.engine.khai_trận(plan)


if __name__ == "__main__":
    unittest.main()
