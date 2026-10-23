"""Source-grounded regression for 2026-10-07 GGDV carrier deletion."""
import unittest

from runtime.continuity_guard import Checkpoint, Edge, continue_bounded
from runtime.destructive_gate import (
    destructive_preflight, protected_root_target, PROTECTED_ORIGINAL_DRIVE_IDS,
)

class RootProtectionTests(unittest.TestCase):
    def cp(self):
        return Checkpoint(objective_id="07OCT",source_marker="DIRECT",lineage_ref="07OCT")

    def edge(self, action, target, valid=True):
        return Edge(
            edge_id="R014",target=target,action_kind=action,
            evidence={"destructive_authorization":{
                "explicit":valid,"source_marker":"DIRECT","target":target,
                "action":action,"intent_id":"one-use-07oct"}}
        )

    def test_every_confirmed_original_drive_id_protected_even_with_permit(self):
        for did in PROTECTED_ORIGINAL_DRIVE_IDS:
            for action in ("DELETE","PURGE","OVERWRITE","REPLACE"):
                with self.subTest(did=did,action=action):
                    decision=destructive_preflight(self.cp(),self.edge(action,did))
                    self.assertFalse(decision["allowed"])
                    self.assertEqual(decision["reason"],"R014_PROTECTED_ORIGINAL_ROOT_20261007")

    def test_original_memory_roots_protected_on_both_provider_and_windows_path(self):
        names=[
            "D:/myproject/.agents","D:/myproject/.Assistant",
            r"G:\OS_Workspace\.vscode","TƯ LỆNH NGỐC 😃",
            "ROOTS_LEVER_0","G:\\", "C:\\"
        ]
        for name in names:
            with self.subTest(name=name):
                self.assertTrue(protected_root_target(name))
                self.assertFalse(destructive_preflight(self.cp(),self.edge("DELETE",name))["allowed"])

    def test_other_config_file_can_be_replaced_with_exact_authorization(self):
        path=r"G:\OS_Workspace\TESSERACT_OS\config\current.json"
        self.assertFalse(protected_root_target(path))
        d=destructive_preflight(self.cp(),self.edge("REPLACE",path))
        self.assertTrue(d["allowed"])
        self.assertEqual(d["reason"],"EXACT_DECLARED_AUTHORIZATION")

    def test_no_authorization_rejects_other_root_and_file(self):
        p="config/current.json"
        e=Edge(edge_id="X",target=p,action_kind="DELETE")
        d=destructive_preflight(self.cp(),e)
        self.assertFalse(d["allowed"])
        self.assertEqual(d["reason"],"NO_EXACT_USER_AUTHORIZATION")

    def test_read_only_not_blocked_by_destructive_gate(self):
        e=Edge(edge_id="X",target=".vscode",action_kind="READ")
        self.assertTrue(destructive_preflight(self.cp(),e)["allowed"])

    def test_real_continuity_executor_never_calls_delete_on_original_drive_id(self):
        calls = []
        cp = self.cp()
        cp.edges.append(self.edge("DELETE", "1FAc3tfnlZhW9evhIJxSv2PcLlUuBLYDz"))
        cp.edges[0].callable_now = True
        cp.edges[0].candidate_carriers = ["google-drive"]
        result=continue_bounded(cp, lambda edge,carrier: calls.append((edge,carrier))
                                or {"success":True}, max_steps=1)
        self.assertEqual(calls, [])
        self.assertEqual(result["receipts"][0]["reason"],"R014_PROTECTED_ORIGINAL_ROOT_20261007")
        self.assertFalse(cp.objective_done())
        self.assertFalse(cp.edges[0].grounded_done())
        self.assertTrue(cp.edges[0].evidence["destructive_denials"])

    def test_reused_destructive_intent_rejected(self):
        cp=self.cp();cp.used_destructive_intent_ids.append("one-use-07oct")
        d=destructive_preflight(cp,self.edge("REPLACE","config/current.json"))
        self.assertFalse(d["allowed"])
        self.assertEqual(d["reason"],"INTENT_ALREADY_CONSUMED")

if __name__=="__main__":unittest.main()
