import unittest, tempfile, pathlib, json, shutil
import source_bridge as b
from administrator_tools_mcp import handle, TOOLS
class SourceBridgeTest(unittest.TestCase):
 def test_ten_directories(self): self.assertEqual(len(b.load_inventory()['folders']),10)
 def test_seventy_one_entries(self): self.assertEqual(sum(x['observed_direct_children'] for x in b.load_inventory()['folders']),71)
 def test_distinct_ids(self): self.assertEqual(len({x['id'] for x in b.load_inventory()['folders']}),10)
 def test_actor_independent(self): self.assertFalse(b.load_inventory()['actor_model_rule']['identity_equivalence'])
 def test_imports_verifiable(self): self.assertTrue(b.verify_carried_tools()['all_match'])
 def test_imports_five_real_scripts(self): self.assertEqual(len(b.verify_carried_tools()['tool_files']),5)
 def test_detect_codex_goal(self): self.assertEqual(b.route('Đưa .codex công cụ về Tools và dọn dẹp')['objective'],'CODEX_TO_ADMINISTRATOR_TOOLS')
 def test_inference(self): self.assertIn('inference',b.route('llama inference')['code'])
 def test_anchor(self): self.assertEqual(b.read_events()['integrity'],'PASS')
 def test_unfinished_kept(self): self.assertFalse(b.read_events()['task_complete'])
 def test_tamper_event_detected(self):
  with tempfile.TemporaryDirectory() as d:
   q=pathlib.Path(d);shutil.copy(b.ROOT/'CAUSAL_REENTRY_EVENTS.jsonl',q/'CAUSAL_REENTRY_EVENTS.jsonl')
   s=(q/'CAUSAL_REENTRY_EVENTS.jsonl').read_text();(q/'CAUSAL_REENTRY_EVENTS.jsonl').write_text(s.replace('Mày đã đưa','Mày đã xóa'))
   with self.assertRaises(ValueError): b.read_events(q)
 def test_mcp_integration(self):
  res=handle({'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'administrator_tools.causal_reentry','arguments':{}}},pathlib.Path('.'))
  self.assertFalse(res['result']['isError'])
 def test_mcp_inventory(self):
  self.assertIn('administrator_tools.source_inventory',[x['name'] for x in TOOLS])
if __name__=='__main__': unittest.main()
