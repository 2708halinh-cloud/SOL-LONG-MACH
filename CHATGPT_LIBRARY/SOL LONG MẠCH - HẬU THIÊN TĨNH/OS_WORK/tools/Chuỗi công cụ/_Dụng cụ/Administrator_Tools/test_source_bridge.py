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
 def test_readback_creates_agent_next(self):
  x=b.read_events();self.assertTrue(x['report_only_warning_active']);self.assertEqual(x['next_actor'],'AGENT')
  self.assertGreaterEqual(x['verified_migrated_batch_files'],5)
  self.assertTrue(x['next_agent'].startswith('REVIEW_CODEX_SKILLS'))
 def test_provider_archive_receipt_has_exact_five(self):
  x=b.read_events();self.assertEqual(x['verified_migrated_batch_files'],5)
 def test_completion_claim_cannot_be_faked(self):
  with tempfile.TemporaryDirectory() as d:
   q=pathlib.Path(d)
   for f in ['CAUSAL_REENTRY_EVENTS.jsonl','source_carriers.json']:
    shutil.copy(b.ROOT/f,q/f)
   shutil.copytree(b.ROOT/'codex_tools',q/'codex_tools')
   entries=[json.loads(x) for x in (q/'CAUSAL_REENTRY_EVENTS.jsonl').read_text().splitlines()]
   e={'event_id':'FORGED_DONE','type':'REPORT','task_complete':True}
   import hashlib
   prev=entries[-1]['entry_hash'];payload=json.dumps(e,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
   entries.append({'prev_hash':prev,'entry_hash':hashlib.sha256(prev.encode()+payload).hexdigest(),'event':e})
   (q/'CAUSAL_REENTRY_EVENTS.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in entries)+'\n')
   with self.assertRaisesRegex(ValueError,'PREMATURE_COMPLETION_CLAIM'): b.read_events(q)
 def test_bin_sha_verified(self):
  self.assertEqual(b.read_events()['verified_bin_carriers'],2)
 def test_bin_tamper_detected(self):
  with tempfile.TemporaryDirectory() as d:
   q=pathlib.Path(d)
   for f in ['CAUSAL_REENTRY_EVENTS.jsonl','source_carriers.json']:
    shutil.copy(b.ROOT/f,q/f)
   shutil.copytree(b.ROOT/'codex_tools',q/'codex_tools')
   x=q/'codex_tools/bin/codex-default.cjs';x.write_bytes(x.read_bytes()+b'\x00')
   with self.assertRaisesRegex(ValueError,'CODEX_BIN_MISMATCH'): b.read_events(q)
 def test_mcp_integration(self):
  res=handle({'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'administrator_tools.causal_reentry','arguments':{}}},pathlib.Path('.'))
  self.assertFalse(res['result']['isError'])
 def test_mcp_inventory(self):
  self.assertIn('administrator_tools.source_inventory',[x['name'] for x in TOOLS])
if __name__=='__main__': unittest.main()