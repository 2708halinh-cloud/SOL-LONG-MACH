"""Synthetic self-eval for REALITY_STONE and its read-only defence lab."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

import reality_stone as stone
import reality_stone_lab as lab

INDEX = json.loads(Path(__file__).with_name("SKILL_INDEX.json").read_text("utf-8"))

class RealityStoneEvals(unittest.TestCase):
    def test_01_24_skill_ids_are_unique(self):
        r=stone.list_skills(INDEX)
        self.assertEqual(r["skill_count"],24)
        self.assertEqual(len(set(r["skill_ids"])),24)
    def test_02_group_uses_latest_label(self):
        self.assertEqual(INDEX["groups"][0]["id"],"group:Phương pháp Suy luận 10 → 13ms/s")
        self.assertEqual(len(INDEX["groups"][0]["members"]),3)
    def test_03_logic_reaches_ai(self):
        self.assertIn("tri-tue-nhan-tao",stone.trace_skill(INDEX,"lo-gic")["reachable"])
    def test_04_reverse_does_not_claim_inverse(self):
        edges=stone.trace_skill(INDEX,"tri-tue-nhan-tao",depth_limit=1)["relations"]
        self.assertTrue(any(e["traversal"]=="REVERSE_TRAVERSAL_ONLY" for e in edges))
    def test_05_existing_autonomy_pointer_retained(self):
        self.assertIn("tu-chu-va-kien-tri",stone.trace_skill(INDEX,"dau-tranh-noi-tam")["reachable"])
    def test_06_unknown_skill_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"SKILL_NOT_IN_INDEX"):
            stone.trace_skill(INDEX,"not-real")
    def test_07_bounds(self):
        with self.assertRaisesRegex(ValueError,"DEPTH_LIMIT_INVALID"):
            stone.trace_skill(INDEX,"lo-gic",depth_limit=99)
    def test_08_dedup_guard(self):
        copy_index=copy.deepcopy(INDEX)
        copy_index["nodes"][0]["id"]=copy_index["nodes"][1]["id"]
        with self.assertRaisesRegex(ValueError,"DUPLICATE_SKILL_ID"):
            stone.validate_index(copy_index)
    def test_09_path_traversal_guard(self):
        copy_index=copy.deepcopy(INDEX)
        copy_index["nodes"][0]["path"]="_Skills/../../private/SKILL.md"
        with self.assertRaisesRegex(ValueError,"SKILL_PATH_TRAVERSAL"):
            stone.validate_index(copy_index)
    def test_10_untrusted_incident_rejected(self):
        with self.assertRaisesRegex(ValueError,"THREAT_TYPE_NOT_SUPPORTED"):
            stone.audit_event({"threat_type":"execute_payload","source_ref":"synthetic"})
    def test_11_event_without_source_rejected(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_REF_REQUIRED"):
            stone.audit_event({"threat_type":"unusual_resource_use"})
    def test_12_audit_status_never_claims_independent_proof(self):
        r=stone.audit_event({"threat_type":"firmware_integrity_risk",
                             "source_ref":"synthetic-only","evidence_verified":True})
        self.assertEqual(r["status"],"REPORTED_AND_ATTESTED_BY_CALLER")
        self.assertEqual(r["actions_executed"],0)
        self.assertNotIn("synthetic-only",str(r))
    def test_13_all_six_incident_types_are_read_only(self):
        for kind in stone.THREAT_PLANS:
            with self.subTest(kind=kind):
                out=stone.audit_event({"threat_type":kind,"source_ref":"fixture"})
                self.assertEqual(out["actions_executed"],0)
                self.assertFalse(out["mutated"])
    def test_14_only_in_memory_experiments(self):
        x=lab.run_all()
        self.assertEqual(x["count"],6)
        self.assertEqual(x["real_world_targets_touched"],0)
        self.assertTrue(x["no_live_system_mutation"])
    def test_15_code_tampering_detected(self):
        x=lab.integrity_trial()
        self.assertTrue(x["detected"])
        self.assertNotEqual(x["before_hash"],x["after_hash"])
    def test_16_label_poisoning_changes_toy_decision(self):
        x=lab.poisoning_trial()
        self.assertNotEqual(x["clean_prediction"],x["poisoned_prediction"])
        self.assertTrue(x["tamper_detected_by_clean_reference"])
    def test_17_resource_signal_with_no_cpu_burn(self):
        x=lab.resource_trial()
        self.assertEqual(len(x["alerts"]),3)
        self.assertFalse(x["actual_cpu_burn"])
    def test_18_telemetry_discrepancy(self):
        x=lab.telemetry_trial()
        self.assertEqual(x["discrepant_samples"],[2])
        self.assertFalse(x["actual_sensor_opened"])
    def test_19_entropy_not_allegation(self):
        x=lab.opaque_data_trial()
        self.assertGreater(x["opaque_entropy_bits_per_byte"],x["plain_entropy_bits_per_byte"])
        self.assertEqual(x["note"],"HIGH_ENTROPY_IS_NOT_PROOF_OF_RANSOMWARE")
    def test_20_firmware_dummy_not_firmware_mutation(self):
        x=lab.firmware_trial()
        self.assertTrue(x["integrity_mismatch"])
        self.assertFalse(x["actual_firmware_access"])
    def test_21_synthetic_result_does_not_contain_actions(self):
        x=lab.run_all()
        self.assertTrue(all(v["actions_executed"] == 0 for v in x["cases"]))
    def test_22_index_roundtrip_bytes_and_schema(self):
        with tempfile.TemporaryDirectory() as td:
            file=Path(td)/"index.json"
            file.write_text(json.dumps(INDEX,ensure_ascii=False),encoding="utf-8")
            self.assertEqual(stone.load_index(file)["skill_count"],24)

class CredentialHandoffRepairEvals(unittest.TestCase):
    def test_authorized_handoff_is_not_automatically_compromise(self):
        result=stone.review_credential_handoff({
            "user_authorized_handoff":True,
            "existing_secret_policy_known":True,
            "exposure_evidence":"none_verified",
            "assistant_asserted_compromise":True})
        self.assertEqual(result["classification"],"AUTHORIZED_HANDOFF_EXPOSURE_NOT_VERIFIED")
        self.assertTrue(result["incorrect_compromise_inference"])
        self.assertTrue(result["existing_secret_policy_reused"])
        self.assertFalse(result["mutated"])
        self.assertFalse(result["raw_credential_inspected"])

    def test_verified_exposure_changes_result(self):
        result=stone.review_credential_handoff({"exposure_evidence":"verified"})
        self.assertEqual(result["classification"],"EXPOSURE_VERIFIED_BY_DECLARED_EVIDENCE")
        self.assertFalse(result["compromise_independently_verified"])

    def test_stop_overrides_next_action(self):
        result=stone.review_credential_handoff({"user_stop_requested":True,"user_authorized_handoff":True})
        self.assertEqual(result["recommended_next"],"STOP_ACTIONS_NO_CONNECTOR_USE_NO_FURTHER_WRITE")

    def test_rejects_credential_values_not_meta(self):
        with self.assertRaisesRegex(ValueError,"HANDOFF_METADATA_ONLY"):
            stone.review_credential_handoff({"api_key":"example-secret-not-real"})


if __name__=="__main__":
    unittest.main()
