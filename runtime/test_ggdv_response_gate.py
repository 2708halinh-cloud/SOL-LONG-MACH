import unittest
from ggdv_response_gate import inspect_output, select_next_route, prepare_host_response

SOURCE = dict(input_open=True, history_checked=True, history_refs=["UBUBU:event:20261007"],
              source_refs=["Drive:file:root"], type="OP_RESULT", executed=True,
              provider_receipt_ref="provider:receipt-123", target_readback_ref="readback:123",
              readback_matches_expected=True, text="Đã đọc lại ở đích")

class GateTests(unittest.TestCase):
    def test_open_dialogue_freedom(self):
        self.assertTrue(inspect_output(dict(type="DIALOGUE", input_open=True, text="Quan điểm chủ quan của tôi, T003.")).allow_output)
    def test_no_closed_input(self):
        self.assertFalse(inspect_output(dict(type="DIALOGUE", input_open=False)).allow_output)
    def test_history_needed(self):
        p = SOURCE | {"history_checked": False}
        self.assertEqual(inspect_output(p).next_edge,"QUERY_UBUBU_AND_RELATIONAL_HISTORY")
    def test_history_refs_needed(self):
        self.assertFalse(inspect_output(SOURCE | {"history_refs": []}).allow_output)
    def test_source_needed(self):
        self.assertEqual(inspect_output(SOURCE | {"source_refs": []}).next_edge,"BACKTRACE_REAL_SOURCE")
    def test_receipt_needed(self):
        self.assertEqual(inspect_output(SOURCE | {"provider_receipt_ref": ""}).next_edge,"FETCH_PROVIDER_RECEIPT")
    def test_readback_needed(self):
        self.assertEqual(inspect_output(SOURCE | {"target_readback_ref": ""}).next_edge,"READBACK_EXACT_TARGET")
    def test_readback_match_needed(self):
        self.assertEqual(inspect_output(SOURCE | {"readback_matches_expected": False}).next_edge,"TRACE_DIFFERENCE_AND_REPAIR")
    def test_no_fabricated_execution(self):
        self.assertEqual(inspect_output(SOURCE | {"executed": False}).next_edge,"CONTINUE_ACTION_ROUTER")
    def test_progress_without_commit_allowed(self):
        p = SOURCE | {"type":"OP_PROGRESS", "executed":False, "provider_receipt_ref":"",
                      "callable_action_available":False, "operational_task_open":False}
        self.assertTrue(inspect_output(p).allow_output)
    def test_missing_capability_flag_must_not_pass_as_progress(self):
        p = SOURCE | {"type":"OP_PROGRESS", "operational_task_open":True}
        self.assertEqual(inspect_output(p).next_edge, "DISCOVER_EXECUTABLE_ACTIONS")
    def test_open_task_without_action_still_cannot_emit_report(self):
        p = SOURCE | {"type":"OP_PROGRESS", "callable_action_available":False,
                      "operational_task_open":True}
        self.assertEqual(inspect_output(p).next_edge, "CONTINUE_OPEN_TASK")
    def test_open_task_cannot_disguise_report_as_dialogue(self):
        p = SOURCE | {"type":"DIALOGUE", "operational_task_open":True,
                      "user_requested_reply":False}
        self.assertFalse(inspect_output(p).allow_output)
    def test_user_requested_dialogue_preserved(self):
        p = SOURCE | {"type":"DIALOGUE", "operational_task_open":True,
                      "user_requested_reply":True}
        self.assertTrue(inspect_output(p).allow_output)
    def test_real_result_allowed(self):
        self.assertTrue(inspect_output(SOURCE).allow_output)
    def test_unverified_result_is_silent(self):
        emitted=[]
        d=prepare_host_response(SOURCE, emitted.append)
        self.assertFalse(d.allow_output)
        self.assertEqual(d.next_edge, "VERIFY_REAL_RECEIPT")
        self.assertEqual(emitted,[])
    def test_corroborated_result_emitted_once(self):
        emitted=[]
        d=prepare_host_response(SOURCE, emitted.append, verify_evidence=lambda p: p is SOURCE)
        self.assertTrue(d.allow_output)
        self.assertEqual(emitted,[SOURCE['text']])
    def test_untrusted_verifier_is_rejected(self):
        emitted=[]
        d=prepare_host_response(SOURCE, emitted.append, verify_evidence=lambda _: False)
        self.assertFalse(d.allow_output)
        self.assertEqual(emitted,[])
    def test_progress_does_not_replace_callable_action(self):
        p = SOURCE | {"type":"OP_PROGRESS","callable_action_available":True}
        emitted=[]
        d=prepare_host_response(p, emitted.append)
        self.assertFalse(d.allow_output)
        self.assertEqual(d.next_edge,"CONTINUE_CALLABLE_ACTION")
        self.assertEqual(emitted,[])
    def test_false_result_silent(self):
        emitted=[]
        d=prepare_host_response(SOURCE | {"executed":False}, emitted.append)
        self.assertFalse(d.allow_output)
        self.assertEqual(emitted,[])
    def test_fallback_doesnt_depend_on_windows(self):
        routes={"ONLINE_DEVICE":False,"PROJECT_CODEX":True,"LIBRARY":True}
        self.assertEqual(select_next_route(routes),"PROJECT_CODEX")
    def test_fallback_prioritizes_personal(self):
        routes={"ONLINE_PERSONAL_TOOL":True,"ONLINE_DEVICE":True}
        self.assertEqual(select_next_route(routes),"ONLINE_PERSONAL_TOOL")
    def test_no_fake_route(self):
        self.assertIsNone(select_next_route({}))
    def test_text_not_censored(self):
        self.assertTrue(inspect_output(SOURCE | {"text":"Anh sẽ... NEVER AUTO UNKNOWN"}).allow_output)

if __name__=="__main__":
    unittest.main()
