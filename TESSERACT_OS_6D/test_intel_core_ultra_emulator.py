import unittest
from runtime.intel_core_ultra_emulator import load_registry, get_profile, plan_task_slots
class IntelCoreUltraProfileTests(unittest.TestCase):
    def test_registry_contains_30_profiles(self):
        self.assertEqual(len(load_registry()["profiles"]), 30)
    def test_251hx_matches_supplied_catalog(self):
        p=get_profile("Intel Core Ultra 7 processor 251HX")
        self.assertEqual((p.cores,p.reported_max_turbo_ghz,p.smart_cache_mb,p.integrated_gpu),(18,5.1,30,"Intel Graphics"))
        self.assertFalse(p.source_verified)
    def test_missing_gpu_not_inferred(self):
        self.assertIsNone(get_profile("Intel Core Ultra 5 processor 250KF Plus").integrated_gpu)
    def test_slot_plan(self):
        p=plan_task_slots("Intel Core Ultra 7 processor 251HX",25)
        self.assertEqual((p["planned_concurrent_tasks"],p["queued_tasks"]),(18,7))
        self.assertFalse(p["gpu_execution_enabled"])
        self.assertFalse(p["hardware_equivalence_claim"])
    def test_negative_tasks_rejected(self):
        with self.assertRaises(ValueError): plan_task_slots("Intel Core Ultra 7 processor 251HX",-1)
if __name__=="__main__": unittest.main()
