import unittest

from runtime.digital_nervous_system import (
    Interneuron,
    MotorNeuron,
    SensoryNeuron,
    run_cognitive_loop,
)


class DigitalNervousSystemTests(unittest.TestCase):
    def setUp(self):
        self.sensory = SensoryNeuron()
        self.interneuron = Interneuron()
        self.motor = MotorNeuron()

    def test_sensory_signal_keeps_provenance_and_does_not_infer_emotion_from_caps(self):
        signal = self.sensory.receive(
            modality="text",
            source_ref="chat://turn/1",
            observed_at="2026-11-05T10:00:00+07:00",
            content="I NEED THIS NOW",
        )
        self.assertEqual(signal.source_ref, "chat://turn/1")
        self.assertEqual(signal.features["uppercase_ratio"], 1.0)
        self.assertNotIn("emotion", signal.features)

    def test_interneuron_keeps_emotion_as_scored_hypothesis(self):
        signal = self.sensory.receive(
            modality="text",
            source_ref="chat://turn/2",
            observed_at="2026-11-05T10:01:00+07:00",
            content="I'm frustrated",
        )
        state = self.interneuron.integrate(
            signal,
            memory_refs=["memory://preference/1"],
            hypotheses={"frustration": 0.8, "urgency": 0.4},
            strategy="brief_support",
        )
        self.assertEqual(state.memory_refs, ("memory://preference/1",))
        self.assertEqual(state.hypotheses["frustration"], 0.8)
        self.assertEqual(state.strategy, "brief_support")

    def test_motor_rejects_command_without_receipt_and_independent_readback(self):
        result = self.motor.dispatch(
            action={"kind": "mute_notifications"},
            executor=lambda action: {"executed": True},
        )
        self.assertFalse(result.success)
        self.assertEqual(result.state, "UNVERIFIED")

    def test_motor_accepts_only_receipted_observed_and_consistent_action(self):
        result = self.motor.dispatch(
            action={"kind": "mute_notifications"},
            executor=lambda action: {
                "executed": True,
                "receipt_ref": "receipt://action/1",
                "readback": {"verified": True, "state_consistent": True},
            },
        )
        self.assertTrue(result.success)
        self.assertEqual(result.state, "VERIFIED")

    def test_cognitive_loop_returns_all_three_layers_and_preserves_open_failure(self):
        signal = self.sensory.receive(
            modality="text",
            source_ref="chat://turn/3",
            observed_at="2026-11-05T10:02:00+07:00",
            content="Please help",
        )
        out = run_cognitive_loop(
            signal,
            self.interneuron,
            self.motor,
            strategy="respond_briefly",
            hypotheses={"request_for_help": 0.9},
            executor=lambda action: {"executed": True},
        )
        self.assertEqual(out["layers"], ["SENSORY", "INTERNEURON", "MOTOR"])
        self.assertFalse(out["motor"].success)
        self.assertEqual(out["state"], "OPEN_MOTOR_READBACK")


if __name__ == "__main__":
    unittest.main()
