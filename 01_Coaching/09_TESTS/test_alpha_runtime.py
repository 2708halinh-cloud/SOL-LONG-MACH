import json, sqlite3, tempfile, unittest
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
M=Path(__file__).resolve().parents[1]/"11_RUNTIME_ALPHA"/"alpha_runtime.py"
s=spec_from_file_location("alpha",M); alpha=module_from_spec(s); s.loader.exec_module(alpha)
class AlphaTests(unittest.TestCase):
 def test_json_ids_actor(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"a.json"; p.write_text(json.dumps({"session_id":"S","conversation_id":"C","project_id":"P","template_id":"T","actor":"MEI"}),encoding="utf-8")
   r=alpha.inspect_carrier(str(p)); self.assertEqual(r["status"],"READBACK_VERIFIED"); self.assertEqual(r["metadata"]["identifiers"]["session_id"],["S"]); self.assertEqual(r["metadata"]["explicit_actor_labels"][0]["layer"],"02_MEI_SELF_DESCRIPTION_ACTION")
 def test_sqlite_readonly_ids_only(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"db.sqlite"; c=sqlite3.connect(p); c.execute("create table x(session_id text, conversation_id text, body text)"); c.execute("insert into x values('s','c','secret body')"); c.commit(); c.close()
   r=alpha.inspect_carrier(str(p)); self.assertEqual(r["status"],"READBACK_VERIFIED"); self.assertEqual(r["metadata"]["tables"][0]["identifiers"]["session_id"],["s"]); self.assertNotIn("secret body",json.dumps(r))
 def test_expected_hash_mismatch(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"a.json"; p.write_text('{"session_id":"x"}'); self.assertEqual(alpha.inspect_carrier(str(p),"0"*64)["status"],"HASH_MISMATCH")
 def test_unknown_actor_partial(self): self.assertEqual(alpha.classify_actor("other agent"),("UNKNOWN","PARTIAL"))
 def test_tool_readback_required(self):
  with self.assertRaises(ValueError): alpha.record_tool_readback("","x","now","OK")
  self.assertEqual(alpha.record_tool_readback("tool","ref","time","verified")["layer"],"04_TOOL_READBACK")
