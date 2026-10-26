import json
import tempfile
import unittest
from pathlib import Path
from runtime.intel_core_ultra_emulator import load_registry, get_profile, plan_task_slots

class IntelCoreUltraProfileTests(unittest.TestCase):
    def test_registry_contains_user_catalog_profiles(self):
        data = load_registry()
        self.assertGreaterEqual(len(data["profiles"]), 31)

    def test_251hx_profile_matches_supplied_catalog(self):
        p = get_profile("Intel Core Ultra 7 processor 251HX")
        self.assertEqual(p.cores, 18)
        self.assertEqual(p.reported_max_turbo_ghz, 5.1)
        self.assertEqual(p.smart_cache_mb, 30)
        self.assertEqual(p.integrated_gpu, "Intel Graphics")
        self.assertFalse(p.source_verified)

    def test_f_model_does_not_infer_gpu(self):
        p = get_profile("Intel Core Ultra 5 processor 250KF Plus")
        self.assertIsNone(p.integrated_gpu)

    def test_265u_preserves_unprovided_gpu_as_unknown(self):
        p = get_profile("Intel Core Ultra 7 265U")
        self.assertEqual(p.cores, 12)
        self.assertEqual(p.reported_max_turbo_ghz, 5.3)
        self.assertEqual(p.smart_cache_mb, 12)
        self.assertIsNone(p.integrated_gpu)
        self.assertEqual(p.gpu_status, "NOT_PROVIDED_IN_USER_LIST")

    def test_slot_planning_is_bounded_and_disclaims_hardware_equivalence(self):
        plan = plan_task_slots("Intel Core Ultra 7 processor 251HX", 25)
        self.assertEqual(plan["planned_concurrent_tasks"], 18)
        self.assertEqual(plan["queued_tasks"], 7)
        self.assertFalse(plan["gpu_execution_enabled"])
        self.assertFalse(plan["hardware_equivalence_claim"])

    def test_negative_task_count_rejected(self):
        with self.assertRaises(ValueError):
            plan_task_slots("Intel Core Ultra 7 processor 251HX", -1)

if __name__ == "__main__":
    unittest.main()
