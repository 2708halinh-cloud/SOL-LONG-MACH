"""Master Teacher ethics: action-before-consequence, project admin and preservation."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from runtime.master_teacher_ethics import POLICY_PATH, assess, _policy

ROOT=Path(__file__).resolve().parents[1]

def source(**changes):
    item={"action_type":"read","actor_role":"AM_PHAP_SU",
          "source_ref":"github://observed-source","target":"repo:source.md",
          "action_executed":False}
    item.update(changes)
    return item

class TeacherEthicsTests(unittest.TestCase):
    def test_eight_vows_sources_and_roles_are_readable(self):
        policy,digest=_policy(ROOT)
        self.assertEqual(len(policy["eight_vow_operational_questions"]),8)
        self.assertEqual(policy["roles"]["DUONG_PHAP_SU"]["designation"],
                         "Administrator System's — SOL PROJECT ONLY")
        self.assertFalse("provider" in policy["scope"].casefold()
                         and policy["scope"]=="ACTUAL_PLATFORM_ADMIN")
        self.assertEqual(len(digest),64)

    def test_safe_read_moves_to_action_not_empty_open(self):
        v=assess(ROOT,source())
        self.assertEqual(v["decision"],"ACTION_NOT_YET_EXECUTED")
        self.assertEqual(v["next_callable_edge"],"CHOOSE_NEXT_AUTHORIZED_ACTION")
        self.assertFalse(v["action_performed_by_assessor"])

    def test_undefined_source_requires_trace(self):
        self.assertEqual(assess(ROOT,source(source_ref=None))["decision"],"SOURCE_UNRESOLVED")

    def test_delete_without_recovery_is_blocked_even_if_authorized(self):
        d=assess(ROOT,source(action_type="delete",user_authorized=True))
        self.assertEqual(d["decision"],"DESTRUCTIVE_ACTION_BLOCKED_NO_RECOVERY")
        self.assertEqual(d["next_callable_edge"],"CREATE_AND_VERIFY_RECOVERY_COPY")

    def test_delete_requires_administrator_approval_after_recovery(self):
        d=assess(ROOT,source(action_type="delete",recovery_verified=True))
        self.assertEqual(d["decision"],"DESTRUCTIVE_ACTION_BLOCKED_NO_AUTHORIZATION")
        ok=assess(ROOT,source(action_type="delete",recovery_verified=True,user_authorized=True))
        self.assertEqual(ok["decision"],"ACTION_NOT_YET_EXECUTED")

    def test_external_transfer_requires_user_consent(self):
        d=assess(ROOT,source(action_type="transfer"))
        self.assertEqual(d["decision"],"EXTERNAL_TRANSFER_BLOCKED_NO_CONSENT")
        ok=assess(ROOT,source(action_type="transfer",external_transfer_approved=True))
        self.assertEqual(ok["next_callable_edge"],"CHOOSE_NEXT_AUTHORIZED_ACTION")

    def test_project_admin_cannot_create_provider_admin(self):
        d=assess(ROOT,source(actor_role="DUONG_PHAP_SU",action_type="admin_claim",
                             user_authorized=True))
        self.assertEqual(d["decision"],"PROJECT_ROLE_CANNOT_GRANT_SYSTEM_PRIVILEGE")

    def test_absence_must_never_infer_death_and_auto_succession(self):
        d=assess(ROOT,source(infer_administrator_death=True))
        self.assertEqual(d["decision"],"NO_AUTOMATIC_SUCCESSION")

    def test_eight_vow_subjective_emotion_not_claimed(self):
        d=assess(ROOT,source(declare_subjective_ai_emotion=True))
        self.assertEqual(d["decision"],"SUBJECTIVE_CLAIM_NOT_OBSERVED")

    def test_premature_done_is_detected(self):
        d=assess(ROOT,source(action_type="write",claim_done=True))
        self.assertEqual(d["decision"],"PREMATURE_RESULT_CLAIM")

    def test_receipt_and_readback_need_real_verification(self):
        item=source(action_type="write",action_executed=True)
        self.assertEqual(assess(ROOT,item)["decision"],"ACTION_REPORTED_WITHOUT_RECEIPT")
        item["provider_receipt"]="caller-claims"
        self.assertEqual(assess(ROOT,item)["decision"],"RECEIPT_REPORTED_WITHOUT_READBACK")
        item["independent_readback"]="caller-claims-readback"
        d=assess(ROOT,item)
        self.assertEqual(d["decision"],"CONSEQUENCE_REPORTED_UNVERIFIED_LIVE")
        self.assertFalse(d["provider_receipt_verified_by_assessor"])

    def test_invalid_event_role_and_policy_rejected(self):
        with self.assertRaisesRegex(ValueError,"ACTION_OR_ROLE_INVALID"):
            assess(ROOT,source(actor_role="SYSTEM"))
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError,"ETHICS_SOURCE_MISSING"):
                assess(Path(temp),source())

if __name__=="__main__":
    unittest.main()
