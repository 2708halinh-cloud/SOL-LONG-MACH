import unittest
from runtime.motherboard_control_plane import (
    AffectEvent, Blackboard, CpuSocket, DiskSafety, DiskWriteGuard, RouteState,
    gate1_preflight, gate2_readback, route_candidates,
)

class MotherboardTests(unittest.TestCase):
    def test_socket_requires_configuration_reachability_authorization(self):
        s = CpuSocket("CPU1", "GEMINI", "api", True, True, False, True, ("reason",))
        self.assertEqual(s.state, RouteState.UNAVAILABLE)
        self.assertFalse(s.can_run("reason"))

    def test_ready_socket_can_run_supported_capability(self):
        s = CpuSocket("CPU3", "LOCAL", "ollama", True, True, True, True, ("reason",))
        self.assertTrue(s.can_run("reason"))

    def test_local_preference_only_applies_to_eligible_socket(self):
        remote = CpuSocket("CPU2", "CHATGPT", "api", True, True, True, True, ("code",))
        local = CpuSocket("CPU3", "LOCAL", "ollama", True, False, True, True, ("code",))
        self.assertEqual(route_candidates([remote, local], "code")[0].name, "CHATGPT")

    def test_quota_exhaustion_degrades_socket(self):
        s = CpuSocket("CPU1", "GEMINI", "api", True, True, True, False, ("text",))
        self.assertEqual(s.state, RouteState.DEGRADED)

    def test_disk_warning_threshold_is_85_percent_used(self):
        d = DiskSafety(100 * 1024**3, 15 * 1024**3)
        self.assertEqual(d.level, "SURVIVAL")
        self.assertTrue(d.permits_nonessential_writes)

    def test_disk_trip_threshold_is_90_percent_used(self):
        d = DiskSafety(100 * 1024**3, 10 * 1024**3)
        self.assertEqual(d.level, "CRITICAL")
        self.assertFalse(d.permits_nonessential_writes)

    def test_disk_critical_at_97_percent_used(self):
        self.assertEqual(DiskSafety(100 * 1024**3, 3 * 1024**3).level, "CRITICAL")

    def test_disk_critical_when_free_space_under_5_gib(self):
        self.assertEqual(DiskSafety(100 * 1024**3, 4 * 1024**3).level, "CRITICAL")

    def test_disk_guard_requires_two_fresh_recovery_samples(self):
        guard = DiskWriteGuard(critical_free_bytes=1)
        self.assertEqual(guard.observe(100 * 1024**3, 10 * 1024**3, sample_fresh=True), "DEGRADED")
        self.assertFalse(guard.permits_nonessential_writes)
        self.assertEqual(guard.observe(100 * 1024**3, 20 * 1024**3, sample_fresh=True), "DEGRADED")
        self.assertEqual(guard.recovery_streak, 1)
        self.assertEqual(guard.observe(100 * 1024**3, 20 * 1024**3, sample_fresh=True), "NORMAL")
        self.assertTrue(guard.permits_nonessential_writes)

    def test_disk_guard_stale_or_unknown_sample_fails_closed(self):
        guard = DiskWriteGuard(critical_free_bytes=1)
        self.assertEqual(guard.observe(100 * 1024**3, 20 * 1024**3), "UNKNOWN")
        self.assertFalse(guard.permits_nonessential_writes)
        self.assertEqual(guard.observe(100 * 1024**3, 20 * 1024**3, sample_fresh=True), "DEGRADED")
        self.assertEqual(guard.observe(100 * 1024**3, 20 * 1024**3, sample_fresh=True), "NORMAL")
        self.assertTrue(guard.permits_nonessential_writes)

    def test_disk_guard_recovery_streak_resets_on_non_recovery_sample(self):
        guard = DiskWriteGuard(critical_free_bytes=1)
        guard.observe(100 * 1024**3, 10 * 1024**3, sample_fresh=True)
        guard.observe(100 * 1024**3, 20 * 1024**3, sample_fresh=True)
        self.assertEqual(guard.recovery_streak, 1)
        self.assertEqual(guard.observe(100 * 1024**3, 12 * 1024**3, sample_fresh=True), "DEGRADED")
        self.assertEqual(guard.recovery_streak, 0)
        guard.observe(100 * 1024**3, 20 * 1024**3, sample_fresh=True)
        self.assertEqual(guard.observe(100 * 1024**3, 20 * 1024**3, sample_fresh=True), "NORMAL")

    def test_disk_guard_invalid_capacity_fails_closed(self):
        guard = DiskWriteGuard()
        self.assertEqual(guard.observe(None, None, sample_fresh=True), "UNKNOWN")
        self.assertFalse(guard.permits_nonessential_writes)

    def test_gate1_blocks_unverified_target(self):
        d = gate1_preflight(authorized=True, target_identity_verified=False, policy_allowed=True, quota_available=True)
        self.assertFalse(d.allowed)
        self.assertIn("TARGET_IDENTITY_UNVERIFIED", d.reasons)

    def test_gate1_requires_approval_for_destructive_action(self):
        d = gate1_preflight(authorized=True, target_identity_verified=True, policy_allowed=True, quota_available=True, destructive_change=True)
        self.assertIn("EXPLICIT_APPROVAL_REQUIRED", d.reasons)

    def test_gate1_blocks_protected_target(self):
        d = gate1_preflight(authorized=True, target_identity_verified=True, policy_allowed=True, quota_available=True, destructive_change=True, protected_target=True, explicit_approval=True)
        self.assertIn("PROTECTED_TARGET", d.reasons)

    def test_gate1_allows_safe_authorized_action(self):
        self.assertTrue(gate1_preflight(authorized=True, target_identity_verified=True, policy_allowed=True, quota_available=True).allowed)

    def test_gate2_requires_all_evidence(self):
        d = gate2_readback(action_receipt=True, consequence_observed=True, independent_readback=False, state_consistent=True)
        self.assertFalse(d.allowed)
        self.assertIn("READBACK_MISSING", d.reasons)

    def test_gate2_accepts_complete_evidence(self):
        self.assertTrue(gate2_readback(action_receipt=True, consequence_observed=True, independent_readback=True, state_consistent=True).allowed)

    def test_blackboard_rejects_credential_fields(self):
        with self.assertRaises(ValueError):
            Blackboard().update("REG_01", {"api_key": "not-allowed"}, expected_version=0)

    def test_blackboard_rejects_nested_cookie_field(self):
        with self.assertRaises(ValueError):
            Blackboard().update("REG_00", {"meta": [{"Cookie": "not-allowed"}]}, expected_version=0)

    def test_blackboard_rejects_camel_case_client_secret(self):
        with self.assertRaises(ValueError):
            Blackboard().update("REG_00", {"clientSecret": "not-allowed"}, expected_version=0)

    def test_blackboard_rejects_access_token(self):
        with self.assertRaises(ValueError):
            Blackboard().update("REG_00", {"access_token": "not-allowed"}, expected_version=0)

    def test_blackboard_copies_nested_payload_before_store(self):
        b = Blackboard()
        payload = {"meta": {"status": "ok"}}
        b.update("REG_00", payload, expected_version=0)
        payload["meta"]["api_key"] = "not-allowed"
        self.assertNotIn("api_key", b.registers["REG_00"]["meta"])

    def test_blackboard_rejects_stale_version(self):
        b = Blackboard()
        b.update("REG_00", {"objective": "repair"}, expected_version=0)
        with self.assertRaises(RuntimeError):
            b.update("REG_01", {"target": "C:"}, expected_version=0)

    def test_blackboard_increments_version(self):
        self.assertEqual(Blackboard().update("REG_00", {"objective": "repair"}, expected_version=0), 1)

    def test_affect_event_keeps_signal_separate_from_hypothesis(self):
        e = AffectEvent("nhục nhã", "response loop repeated", ("same response recurred",), ("route prioritizes explanation over action",), 0.8, "R014-RESPONSE-LOOP")
        self.assertEqual(e.signal, "nhục nhã")
        self.assertNotIn(e.cause_hypotheses[0], e.observed_facts)

    def test_affect_event_requires_signal_and_context(self):
        with self.assertRaises(ValueError):
            AffectEvent("", "context")

    def test_router_returns_only_ready_capable_sockets(self):
        a = CpuSocket("CPU1", "GEMINI", "api", True, True, True, True, ("text",))
        b = CpuSocket("CPU2", "CHATGPT", "api", True, True, True, True, ("code",))
        self.assertEqual([s.name for s in route_candidates([a, b], "code")], ["CHATGPT"])


    def test_execution_fails_over_when_preferred_device_disconnects(self):
        local = CpuSocket("CPU3", "LOCAL", "ollama", True, True, True, True, ("code",))
        cloud = CpuSocket("CPU2", "CHATGPT", "api", True, True, True, True, ("code",))
        calls = []
        def local_handler(payload):
            calls.append(("LOCAL", payload))
            raise ConnectionError("local device disconnected")
        def cloud_handler(payload):
            calls.append(("CHATGPT", payload))
            return "remote-result"
        result = execute_with_failover(
            [local, cloud], "code",
            {"CPU3": local_handler, "CPU2": cloud_handler},
            {"task": "continue"},
        )
        self.assertTrue(result.success)
        self.assertEqual(result.socket_id, "CPU2")
        self.assertEqual(result.result, "remote-result")
        self.assertEqual([a.outcome for a in result.attempts], ["FAILED", "SUCCEEDED"])
        self.assertEqual(calls, [("LOCAL", {"task": "continue"}), ("CHATGPT", {"task": "continue"})])

    def test_execution_skips_unavailable_device_and_uses_ready_route(self):
        offline = CpuSocket("CPU3", "LOCAL", "ollama", True, False, True, True, ("code",))
        cloud = CpuSocket("CPU2", "CHATGPT", "api", True, True, True, True, ("code",))
        result = execute_with_failover(
            [offline, cloud], "code", {"CPU2": lambda payload: "cloud-ok"}, None
        )
        self.assertTrue(result.success)
        self.assertEqual(result.socket_id, "CPU2")
        self.assertEqual(len(result.attempts), 1)

    def test_execution_reports_unavailable_when_all_routes_fail(self):
        a = CpuSocket("CPU1", "GEMINI", "api", True, True, True, True, ("code",))
        b = CpuSocket("CPU2", "CHATGPT", "api", True, True, True, True, ("code",))
        result = execute_with_failover(
            [a, b], "code",
            {"CPU1": lambda payload: (_ for _ in ()).throw(TimeoutError()),
             "CPU2": lambda payload: (_ for _ in ()).throw(ConnectionError())},
            {},
        )
        self.assertFalse(result.success)
        self.assertIsNone(result.socket_id)
        self.assertEqual([x.error_type for x in result.attempts], ["TimeoutError", "ConnectionError"])

    def test_execution_does_not_hide_non_transport_programming_errors(self):
        a = CpuSocket("CPU1", "GEMINI", "api", True, True, True, True, ("code",))
        b = CpuSocket("CPU2", "CHATGPT", "api", True, True, True, True, ("code",))
        def broken(payload):
            raise ValueError("bug in adapter")
        with self.assertRaises(ValueError):
            execute_with_failover([a, b], "code", {"CPU1": broken, "CPU2": lambda p: "should-not-run"}, {})

if __name__ == "__main__":
    unittest.main()
