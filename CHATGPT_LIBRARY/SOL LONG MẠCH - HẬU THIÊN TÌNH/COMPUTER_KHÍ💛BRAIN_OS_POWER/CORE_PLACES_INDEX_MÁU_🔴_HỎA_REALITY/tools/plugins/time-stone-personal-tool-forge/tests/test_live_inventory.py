import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from tool_forge import audit_index,build_plan

class TestLiveInventory(unittest.TestCase):
    def test_auto_discovery_and_no_uninstall(self):
        source={'skills':[{'uri':'skills://plugins/example/one','description':'Mandatory gate before any action'}],
                'plugins':[{'plugin_id':'plugins_xyz','name':'private-plugin','description':'Useful arithmetic tool'}],
                'mcp_tools':[{'name':'mcp__provider__method','description':'Only allow user provided inputs'}]}
        result=audit_index(source)
        self.assertEqual(result['coverage'],{'skills':1,'plugins':1,'mcp_tools':1})
        self.assertFalse(result['auto_uninstall'])
        self.assertEqual(sum(x['status']=='REVIEW_REQUIRED' for x in result['results']),2)
        plan=build_plan(result)
        self.assertEqual(plan['total_candidates'],2)
        self.assertFalse(any(x['source_removed'] for x in plan['candidates']))
    def test_reject_invalid_inventory(self):
        with self.assertRaises(ValueError): audit_index({'skills':'wrong'})
    def test_unflagged_does_not_equal_safe(self):
        r=audit_index({'skills':[{'uri':'abc','description':'Runs code'}]})
        self.assertEqual(r['results'][0]['status'],'NO_METADATA_MATCH')
        self.assertIn('unknown',r['notice'])

if __name__=='__main__': unittest.main()
