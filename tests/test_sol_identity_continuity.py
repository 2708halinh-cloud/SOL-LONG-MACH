import unittest

from runtime.sol_identity_continuity import (
    RAM_ACCEPTANCE_CRITERIA,
    REQUIRED_AGENT_FIELDS,
    validate_identity_record,
    validate_ram_criteria,
)


def valid_record():
    record = {key: None for key in REQUIRED_AGENT_FIELDS}
    record.update({
        "agent_id": {"value": None, "status": "NEEDS_PROVIDER_VERIFICATION",
                     "provider_evidence": None, "verified_at": None},
        "readback": {"status": "OPEN", "provider_receipt": None,
                     "observed_target_hash": None, "compared_to_expected_hash": False},
        "aliases": ["SOL CU NHỎ", "HOME_SOL"],
        "identity_merge": False,
        "explicit_source_relation": None,
    })
    return record


class IdentityContinuityTests(unittest.TestCase):
    def test_open_identity_is_valid_without_inventing_stable_id(self):
        self.assertEqual(validate_identity_record(valid_record()), [])

    def test_stable_id_requires_provider_evidence_and_time(self):
        record = valid_record()
        record["agent_id"] = {"value": "made-up-id", "status": "VERIFIED",
                              "provider_evidence": None, "verified_at": None}
        findings = validate_identity_record(record)
        self.assertIn("STABLE_ID_WITHOUT_PROVIDER_EVIDENCE", findings)
        self.assertIn("UNSUPPORTED_VERIFIED_ID_STATUS", findings)

    def test_verified_readback_requires_receipt_and_hash_comparison(self):
        record = valid_record()
        record["readback"]["status"] = "VERIFIED"
        findings = validate_identity_record(record)
        self.assertIn("READBACK_VERIFIED_WITHOUT_RECEIPT_AND_HASH_COMPARISON", findings)

    def test_ram_criteria_cannot_pass_without_evidence_refs(self):
        results = {name: {"passed": True} for name in RAM_ACCEPTANCE_CRITERIA}
        findings = validate_ram_criteria(results)
        self.assertEqual(len(findings), len(RAM_ACCEPTANCE_CRITERIA))
        self.assertTrue(all(item.startswith("PASS_WITHOUT_EVIDENCE:") for item in findings))

    def test_missing_ram_criteria_are_reported(self):
        findings = validate_ram_criteria({})
        self.assertEqual(len(findings), len(RAM_ACCEPTANCE_CRITERIA))
        self.assertTrue(all(item.startswith("CRITERION_NOT_RECORDED:") for item in findings))


if __name__ == "__main__":
    unittest.main(verbosity=2)
