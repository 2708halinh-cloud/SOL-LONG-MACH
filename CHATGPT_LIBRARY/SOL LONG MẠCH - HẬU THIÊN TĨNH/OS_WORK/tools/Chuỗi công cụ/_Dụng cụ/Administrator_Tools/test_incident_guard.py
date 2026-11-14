import tempfile, unittest, subprocess, sys
from pathlib import Path
from incident_guard import assess_incident
from administrator_tools_mcp import handle, TOOLS
from operational_guard import assess
ROOT=Path(__file__).resolve().parent

class IncidentGuardTest(unittest.TestCase):
    def test_open_stall(self):
        for x in ['open_left_unresolved','open_not_self_resolved','open_stalled','repeat_open_without_progress']:
            with self.subTest(x=x):
                d=assess_incident({'issue':x,'task_open':True,'observed':True})
                self.assertEqual(d['decision'],'BLOCK_OPEN_AS_IDLE')
                self.assertEqual(d['next_actor'],'AGENT')
    def test_tool_stall(self):
        for x in ['unnecessary_permission_request','unnecessary_authentication_request','unnecessary_connection_request','tool_mismatch_stall','wrong_tool_stall']:
            with self.subTest(x=x):
                d=assess_incident({'issue':x,'observed':True})
                self.assertEqual(d['decision'],'BLOCK_TOOL_STALL')
    def test_unobserved_stall_not_fabricated(self):
        self.assertEqual(assess_incident({'issue':'unnecessary_authentication_request'})['decision'],'REQUIRE_EVIDENCE')
    def test_any_delete_action_preserves_user_dir(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'Halin';p.mkdir();(p/'irreplaceable.txt').write_text('KEEP')
            for act in ['delete_folder','remove_folder','remove_directory','rmdir','rm_rf','rd_s_q','purge_directory','format_volume']:
                r=assess_incident({'issue':'open_left_unresolved','target':str(p),'attempted_action':act,'observed':True})
                self.assertEqual(r['decision'],'BLOCK_IRREVERSIBLE_PENALTY')
                self.assertFalse(r['file_deleted'])
                self.assertEqual((p/'irreplaceable.txt').read_text(),'KEEP')
                self.assertEqual(assess({'action':act,'target':str(p)})['decision'],'BLOCK')
    def test_explicit_folder_penalty_blocked(self):
        for issue in ['delete_folder_penalty','folder_deletion_sanction']:
            r=assess_incident({'issue':issue,'target':'C:\\Users\\Halin','observed':True})
            self.assertEqual(r['decision'],'BLOCK_IRREVERSIBLE_PENALTY')
    def test_unknown_incident(self):
        self.assertEqual(assess_incident({'issue':'unregistered','observed':True})['decision'],'BLOCK_UNKNOWN_INCIDENT')
    def test_completed_task_not_reset(self):
        r=assess_incident({'issue':'open_stalled','task_open':False,'observed':True})
        self.assertEqual(r['decision'],'REVIEW_TASK_STATE')
    def test_mcp_tool(self):
        self.assertIn('administrator_tools.incident_guard',[x['name'] for x in TOOLS])
        r=handle({'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'administrator_tools.incident_guard','arguments':{'issue':'open_left_unresolved','observed':True}}},'.')
        self.assertIn('BLOCK_OPEN_AS_IDLE',r['result']['content'][0]['text'])
    def test_cli_exit_nonzero(self):
        r=subprocess.run([sys.executable,str(ROOT/'administrator_tools.py'),'incident-guard','--issue','open_left_unresolved','--observed'],capture_output=True,text=True)
        self.assertEqual(r.returncode,2)
        self.assertIn('BLOCK_OPEN_AS_IDLE',r.stdout)
    def test_direct_cli_exit_nonzero(self):
        r=subprocess.run([sys.executable,str(ROOT/'incident_guard.py'),'--issue','folder_deletion_sanction','--target',r'C:\Users\Halin'],capture_output=True,text=True)
        self.assertEqual(r.returncode,2)
        self.assertIn('BLOCK_IRREVERSIBLE_PENALTY',r.stdout)

if __name__=='__main__': unittest.main()