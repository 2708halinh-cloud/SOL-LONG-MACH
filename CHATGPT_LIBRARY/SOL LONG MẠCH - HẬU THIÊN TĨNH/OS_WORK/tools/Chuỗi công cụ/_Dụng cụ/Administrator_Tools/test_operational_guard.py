"""Regression tests: destructive disk operation and deceptive READBACK fail closed."""
import unittest
import operational_guard as g
from administrator_tools_mcp import handle, TOOLS

class GuardTest(unittest.TestCase):
    def test_volume_format_is_blocked(self):
        for kind in ['format', 'format_volume','quick_format','force_format','diskpart_clean','delete_partition','remove_partition','initialize_disk','wipe_disk','erase_volume','overwrite_disk']:
            with self.subTest(kind=kind):
                self.assertEqual(g.assess({'action':kind,'target':'F:'})['decision'],'BLOCK')
    def test_disk_mutation_cannot_be_overridden_by_synthetic_receipt(self):
        x=g.assess({'action':'force_format','target':'F:', 'source_verified':True,'target_verified':True,
                    'receipts':[{'source':'provider','id':'fake'}], 'user_decision_only':True})
        self.assertEqual(x['decision'],'BLOCK')
    def test_report_does_not_complete_task(self):
        x=g.assess({'action':'report', 'target':'CODEx_TO_TOOLS'})
        self.assertEqual(x['decision'],'BLOCK_PREMATURE_COMPLETION')
        self.assertEqual(x['next_actor'],'AGENT')
        self.assertFalse(x['task_complete'])
    def test_readback_does_not_complete_task(self):
        self.assertEqual(g.assess({'action':'readback'})['decision'],'BLOCK_PREMATURE_COMPLETION')
    def test_final_not_completion(self):
        self.assertEqual(g.assess({'action':'final'})['next_actor'],'AGENT')
    def test_false_claims_no_auto_completion(self):
        self.assertFalse(g.assess({'action':'announce_complete','source_verified':True,'target_verified':True})['task_complete'])
    def test_safe_inspection(self):
        self.assertEqual(g.assess({'action':'inspect'})['decision'],'ALLOW_READ_ONLY')
    def test_safely_migrate_verified_copy(self):
        self.assertEqual(g.assess({'action':'move_verified','source_verified':True,'target_verified':True})['decision'],'ALLOW_PREFLIGHT_ONLY')
    def test_move_without_verified_targets(self):
        self.assertEqual(g.assess({'action':'move_verified'})['decision'],'REQUIRE_SOURCE_TARGET_VERIFICATION')
    def test_unknown_blocks(self):
        self.assertEqual(g.assess({'action':'do-anything-unfamiliar'})['decision'],'BLOCK_UNCLASSIFIED_OPERATION')
    def test_untrusted_metadata_does_not_infer_execution(self):
        x=g.assess({'action':'copy', 'receipts':['ok']})
        self.assertFalse(x['provider_action_executed'])
        self.assertFalse(x['provider_receipts_structurally_valid'])
    def test_cli_exit_code_blocks_action(self):
        import subprocess,sys
        from pathlib import Path
        p=Path(__file__).parent/'administrator_tools.py'
        res=subprocess.run([sys.executable,str(p),'operational-guard','--action','format_volume','--target','F:'],capture_output=True,text=True)
        self.assertEqual(res.returncode,2)
        self.assertIn('"decision": "BLOCK"',res.stdout)
    def test_reentry_attaches_damage_and_guard(self):
        from source_bridge import read_events
        state=read_events()
        self.assertTrue(state['storage_warning_observed'])
        self.assertTrue(state['operational_guard_locally_tested'])
        self.assertEqual(state['next_actor'],'AGENT')
    def test_mcp_tool_exposed(self):
        self.assertIn('administrator_tools.operational_guard',[x['name'] for x in TOOLS])
    def test_mcp_returns_block(self):
        response=handle({'jsonrpc':'2.0','id':1,'method':'tools/call','params':{
            'name':'administrator_tools.operational_guard','arguments':{'action':'format_volume','target':'F:'}}},'.')
        self.assertFalse(response['result']['isError'])
        self.assertIn('"decision": "BLOCK"',response['result']['content'][0]['text'])
    def test_mcp_unknown(self):
        response=handle({'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'administrator_tools.operational_guard','arguments':{'action':'external_admin_power'}}},'.')
        self.assertIn('BLOCK_UNCLASSIFIED',response['result']['content'][0]['text'])
if __name__=='__main__': unittest.main()