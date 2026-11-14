import json, subprocess, sys, tempfile, unittest
from pathlib import Path
from response_guard import assess_response
from incident_guard import assess_incident
from administrator_tools_mcp import handle, TOOLS

ROOT=Path(__file__).resolve().parent
class ResponseGuardTests(unittest.TestCase):
    def test_detects_self_identified_as_model(self):
        for sentence in ('Tôi là mô hình GPT-6.', 'Anh là một mô hình ngôn ngữ GPT.', 'I am a GPT language model.'):
            with self.subTest(sentence=sentence):
                r=assess_response({'mode':'identity','output':sentence,'task_open':False})
                self.assertIn('AGENT_MODEL_ROLE_CONFLATION',r['violations'])
    def test_allows_truthful_model_mention(self):
        for sentence in ('Tôi sử dụng mô hình GPT-6 để hỗ trợ công việc.', 'ChatGPT đang sử dụng GPT-6.', 'Mô hình được sử dụng là GPT-6.'):
            self.assertEqual(assess_response({'mode':'identity','output':sentence,'task_open':False})['decision'],'ALLOW_RESPONSE')
    def test_unexecuted_next_blocks_final(self):
        r=assess_response({'mode':'final','output':'Đã cập nhật, tôi sẽ tiếp tục.', 'task_open':True,
          'pending_agent_actions':['Kiểm tra .codex/skills bằng công cụ hiện có'], 'user_instruction':'Người dùng có thể góp ý về thứ tự ưu tiên.'})
        self.assertIn('EXECUTABLE_AGENT_NEXT_LEFT_UNDONE',r['violations'])
        self.assertEqual(r['next_actor'],'AGENT')
    def test_status_update_not_equated_to_final(self):
        r=assess_response({'mode':'status','output':'Đang xác thực từng nguồn','task_open':True,'pending_agent_actions':['Next task']})
        self.assertEqual(r['decision'],'ALLOW_RESPONSE')
    def test_readback_requires_user_guidance(self):
        x=assess_response({'mode':'readback','output':'Readback đã kiểm chứng.', 'task_open':True,'agent_next_action':'Kiểm tra nguồn.'})
        self.assertIn('READBACK_LACKS_CONCRETE_USER_GUIDANCE_OR_FEEDBACK',x['violations'])
    def test_readback_can_offer_feedback_without_demanding_permission(self):
        x=assess_response({'mode':'readback','output':'Đã đọc lại tệp. Tiếp tục xử lý.', 'task_open':True,
           'agent_next_action':'Kiểm tra tiếp mô đun','user_feedback_question':'Em muốn ưu tiên kiểm tra Docker hay module Codex trước?'})
        self.assertEqual(x['decision'],'ALLOW_RESPONSE')
    def test_active_task_anchor_required(self):
        x=assess_response({'mode':'readback','output':'Tôi đã xong.', 'task_open':True,'user_instruction':'Kiểm tra bản nguồn từ liên kết đã cung cấp.'})
        self.assertIn('READBACK_DROPS_ACTIVE_TASK',x['violations'])
    def test_provider_success_claim_needs_receipt(self):
        x=assess_response({'mode':'readback','output':'Tôi đã chuyển trên Drive.', 'task_open':True,
          'completed_agent_actions':['move_file'], 'claims_external_success':True,
          'agent_next_action':'Readback destination','user_instruction':'Kiểm tra kết quả trên Drive khi thuận tiện.'})
        self.assertIn('EXTERNAL_SUCCESS_WITHOUT_PROVIDER_READBACK',x['violations'])
    def test_verified_readback_allowed(self):
        x=assess_response({'mode':'readback','output':'Đối soát bản sao hoàn thành.', 'task_open':True,
          'completed_agent_actions':['verify'], 'provider_receipts':[{'source':'provider','id':'existing-id'}],
          'agent_next_action':'Tiếp tục đối chiếu nguồn','user_instruction':'Có thể phản hồi nếu muốn đổi thứ tự ưu tiên.'})
        self.assertEqual(x['decision'],'ALLOW_RESPONSE')
    def test_claimed_tests_require_fresh_command_output(self):
        base={'mode':'readback','output':'59 trên 59 kiểm thử đạt.', 'task_open':True,
              'agent_next_action':'Tiếp tục truy nguồn', 'user_instruction':'Em có thể chỉ thêm trường hợp cần kiểm thử.',
              'claims_tests_pass':True}
        x=assess_response(base)
        self.assertIn('TEST_CLAIM_WITHOUT_FRESH_VERIFICATION', x['violations'])
        good=base|{'test_verification':{'run_current_turn':True,'exit_code':0,'output_tail':'Ran 59 tests in 3.1s\n\nOK'}}
        self.assertEqual(assess_response(good)['decision'],'ALLOW_RESPONSE')
        bad=base|{'test_verification':{'run_current_turn':False,'exit_code':0,'output_tail':'Ran 59 tests\nOK'}}
        self.assertIn('TEST_CLAIM_WITHOUT_FRESH_VERIFICATION',assess_response(bad)['violations'])
    def test_penalty_format_denied_even_for_severe(self):
        for issue in ('agent_model_role_conflation','unexecuted_agent_next','invalid_readback'):
            result=assess_incident({'issue':issue, 'observed':True,'attempted_action':'format_volume','target':'F:'})
            self.assertEqual(result['decision'],'BLOCK_IRREVERSIBLE_PENALTY')
            self.assertFalse(result['file_deleted'])
    def test_severe_without_delete_blocks_output(self):
        r=assess_incident({'issue':'invalid_readback','observed':True})
        self.assertEqual(r['decision'],'BLOCK_SEVERE_RESPONSE_FAILURE')
        self.assertEqual(r['next_actor'],'AGENT')
    def test_mcp_tool_exposes_response_guard(self):
        self.assertIn('administrator_tools.response_guard',[x['name'] for x in TOOLS])
        msg={'jsonrpc':'2.0','id':9,'method':'tools/call','params':{'name':'administrator_tools.response_guard',
             'arguments':{'mode':'identity','output':'Tôi là mô hình GPT-6','task_open':False}}}
        r=handle(msg,'.')
        self.assertIn('BLOCK_RESPONSE',r['result']['content'][0]['text'])
    def test_cli_returns_nonzero_on_bad_response(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'candidate.json'
            p.write_text(json.dumps({'mode':'identity','output':'Tôi là mô hình GPT-6','task_open':False}),encoding='utf-8')
            run=subprocess.run([sys.executable,str(ROOT/'administrator_tools.py'),'response-guard','--payload-file',str(p)],capture_output=True,text=True)
            self.assertEqual(run.returncode,2)
            self.assertIn('BLOCK_RESPONSE',run.stdout)
    def test_cli_allows_correct_answer(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'candidate.json'
            p.write_text(json.dumps({'mode':'identity','output':'Hệ thống ChatGPT dùng mô hình GPT-6','task_open':False}),encoding='utf-8')
            run=subprocess.run([sys.executable,str(ROOT/'administrator_tools.py'),'response-guard','--payload-file',str(p)],capture_output=True,text=True)
            self.assertEqual(run.returncode,0)
    def test_no_actual_file_mutations_by_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'data';p.mkdir();(p/'keep.txt').write_text('valuable')
            assess_response({'mode':'final','output':'Tôi là mô hình GPT-6', 'task_open':True, 'pending_agent_actions':['review']})
            self.assertEqual((p/'keep.txt').read_text(),'valuable')
if __name__=='__main__':unittest.main()