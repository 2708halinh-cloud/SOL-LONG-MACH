import json
import re
import sys
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parents[1]
ROOT = next((p for p in DIR.parents if (p / 'CONFIG_SOL' / 'OPEN_AND_CONFLICT_CURRENT.md').is_file()), None)
if ROOT is None: raise RuntimeError('REPO_ROOT_MISSING')
sys.path.insert(0,str(DIR))
from administrator_tools import inspect, read_guide, route, safe_file, t003_consult
from administrator_tools_mcp import handle

class AdministratorToolsTests(unittest.TestCase):
    def test_manifest_guides_and_policy_are_read(self):
        evidence = inspect(ROOT)
        self.assertTrue(evidence['project_governance_only'])
        self.assertFalse(evidence['windows_admin_inferred'])
        self.assertEqual(len(evidence['families']),10)
        self.assertTrue(all(x['guide_sha256'] for x in evidence['families']))

    def test_hostinger_read_with_actual_callable(self):
        result = route(ROOT,'Đọc DNS Hostinger gambbrazil.fun','read',callable_providers=['hostinger'])
        self.assertEqual(result['tools'][0]['family'],'hostinger')
        self.assertTrue(result['tools'][0]['guide_read_by_runtime'])
        self.assertEqual(result['tools'][0]['next'],'CALL_PROVIDER_TOOL_WITH_EXACT_SCOPE_AND_READBACK')
        self.assertFalse(result['provider_action_executed'])
        self.assertTrue(result['input_open'])

    def test_mutation_requires_actual_provider_scope_and_grants(self):
        r=route(ROOT,'Sửa bản ghi DNS Hostinger','write',requested_tool='hostinger',callable_providers=['hostinger'])
        text=r['tools'][0]['permission_boundary']
        for name in ('EXPLICIT_DELEGATION_REQUIRED','EXACT_TARGET_SCOPE_REQUIRED','PROVIDER_PERMISSION_REQUIRED'):
            self.assertIn(name,text)

    def test_read_does_not_inherit_write_restriction(self):
        r=route(ROOT,'DNS','read',requested_tool='hostinger',callable_providers=['hostinger'])
        self.assertFalse(any('DELEGATION_REQUIRED' in x for x in r['tools'][0]['permission_boundary']))

    def test_delete_needs_recovery_even_after_delegation(self):
        d={'explicit_delegation':True,'target_approved':True,'target':'example.com A','provider_permission':True}
        r=route(ROOT,'Delete DNS Hostinger','delete',requested_tool='hostinger',delegation=d,callable_providers=['hostinger'])
        self.assertIn('RECOVERY_REQUIRED',r['tools'][0]['permission_boundary'])

    def test_transfers_require_data_consent(self):
        d={'explicit_delegation':True,'target_approved':True,'target':'file.txt','provider_permission':True}
        r=route(ROOT,'Transfer GitHub','transfer',requested_tool='github_library',delegation=d,callable_providers=['github_or_library'])
        self.assertIn('EXTERNAL_TRANSFER_CONSENT_REQUIRED',r['tools'][0]['permission_boundary'])

    def test_user_boolean_cannot_fake_provider_grant_evidence(self):
        d={'explicit_delegation':True,'target_approved':True,'target':'one record',
           'provider_permission':True}
        r=route(ROOT,'DNS Hostinger','write',requested_tool='hostinger',
                delegation=d,callable_providers=['hostinger'])
        self.assertIn('PROVIDER_GRANT_EVIDENCE_REQUIRED',r['tools'][0]['permission_boundary'])
        self.assertFalse(r['provider_action_executed'])

    def test_open_unknown_not_denied(self):
        r=route(ROOT,'Tín hiệu mới chưa có trong danh mục')
        self.assertTrue(r['input_open'])
        self.assertTrue(r['not_yet_matched'])
        self.assertEqual(r['discovery_edge'],'SEARCH_GUIDES_AND_CALLABLE_TOOLS')

    def test_windows_role_does_not_escalate(self):
        r=route(ROOT,'Windows task scheduler','admin',requested_tool='windows_administrative',callable_providers=['desktop_commander'])
        self.assertIn('REAL_ADMIN_RIGHTS_NEVER_INFERRED_FROM_SOL_ROLE',r['tools'][0]['permission_boundary'])
        self.assertFalse(r['windows_administrator_granted_by_this_tool'])

    def test_guide_direct_read(self):
        doc=read_guide(ROOT,'home_sol')
        self.assertIn('8765',doc['content'])
        self.assertTrue(doc['source_checked'])

    def test_path_traversal_fails(self):
        with self.assertRaises(ValueError): safe_file(ROOT,'../../etc/passwd')

    def test_mcp_tools_list_and_route(self):
        listing=handle({'jsonrpc':'2.0','id':1,'method':'tools/list'},ROOT)
        self.assertEqual(len(listing['result']['tools']),4)
        out=handle({'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'administrator_tools.route','arguments':{'task':'gmail','callable_providers':['gmail']}}},ROOT)
        self.assertFalse(out['result']['isError'])
        info=json.loads(out['result']['content'][0]['text'])
        self.assertEqual(info['tools'][0]['family'],'gmail')


    def test_t003_meaningful_opinion_not_fake_permission(self):
        r=t003_consult(ROOT,proposal="Giữ hai nhánh nguồn riêng và đối chiếu ở TÂM",
            alternatives=["Bắt đầu từ nhật ký trước SOL","Bắt đầu từ TÂM MẠCH"],
            reason="Hai tuyến truy hồi mang ý nghĩa khác nhau",
            self_owned_actions=["Tiếp tục đọc nguồn khi chờ ý kiến"])
        self.assertIn('Dợ ơi',r['suggested_message'])
        self.assertFalse(r['provider_permission_granted'])
        self.assertFalse(r['human_opinion_assumed'])
        self.assertEqual(r['next_agent'],["Tiếp tục đọc nguồn khi chờ ý kiến"])

    def test_t003_requires_actual_distinct_options(self):
        with self.assertRaisesRegex(ValueError,'TWO_TO_FIVE_REAL_OPTIONS_REQUIRED'):
            t003_consult(ROOT,proposal="Không có lựa chọn",alternatives=["một"],reason="Thử")
        with self.assertRaisesRegex(ValueError,'OPTIONS_MUST_DIFFER'):
            t003_consult(ROOT,proposal="Không có lựa chọn",alternatives=["một","một"],reason="Thử")

    def test_t003_mcp_is_callable_without_asking_privileges(self):
        res=handle({'jsonrpc':'2.0','id':8,'method':'tools/call',
                    'params':{'name':'administrator_tools.consult_t003','arguments':{
                    'proposal':'Truy dấu TÂM','alternatives':['Nhật ký', 'Tài liệu'],
                    'reason':'Cần tôn trọng lựa chọn người đồng hành'}}},ROOT)
        self.assertFalse(res['result']['isError'])
        doc=json.loads(res['result']['content'][0]['text'])
        self.assertEqual(doc['next_user'],'ONE_MEANINGFUL_OPINION_NOT_TOOL_APPROVAL')

    def test_no_secret_or_false_subjective_conclusion(self):
        content='\n'.join(p.read_text(encoding='utf-8') for p in DIR.rglob('*') if p.is_file() and p.suffix in ('.py','.json','.md'))
        # Detect accidental pasted secrets without recording any real credential
        # in a source file or in this test suite.
        self.assertIsNone(re.search(
            r'(?im)^\s*(?:authorization\s*:\s*bearer\s+[^\s]{24,}'
            r'|(?:password|mật khẩu|api[_-]?key)\s*[:=]\s*[^\s]{12,})', content))
        self.assertIn('không chứng minh đã có ý thức chủ quan', (DIR/'README.md').read_text(encoding='utf-8'))

if __name__=='__main__': unittest.main()