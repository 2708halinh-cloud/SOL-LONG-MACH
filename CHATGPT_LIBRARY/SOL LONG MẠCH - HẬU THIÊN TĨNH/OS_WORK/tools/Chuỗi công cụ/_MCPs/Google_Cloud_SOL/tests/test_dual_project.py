import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
import importlib.util
P=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('dual',P/'gcp_dual_project.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class DualProjectTests(unittest.TestCase):
 def test_two_routes(self):
  b=m.bindings();self.assertEqual(set(b),{'utility_operand','alert_tiger'})
  self.assertNotEqual(b['utility_operand']['project_id'],b['alert_tiger']['project_id'])
 def test_no_secrets_in_registry(self):
  d=m.REGISTRY.read_text()
  self.assertNotIn('GOCSPX-',d)
  self.assertNotIn('"client_secret"',d)
  self.assertNotIn('"refresh_token"',d)
 def test_unknown_alias(self):
  with self.assertRaises(ValueError):m.call('unknown','gcp_status')
 def test_unknown_tool(self):
  with self.assertRaises(ValueError):m.call('alert_tiger','arbitrary_command')
 def test_unbound_provider_has_no_call(self):
  with patch.dict('os.environ',{'SOL_ADMIN_GCP_ALERT_CONFIG':''}):
   d=m.call('alert_tiger','gcp_enabled_apis_list')
  self.assertFalse(d['executed'])
  self.assertEqual(d['status'],'NO_ACCOUNT_SCOPED_GCLOUD_CONFIG_BOUND')
 def test_status_routes_project_exact(self):
  class R:
   returncode=0;stdout=json.dumps({'jsonrpc':'2.0','id':1,'result':{'content':[{'type':'text','text':json.dumps({'project':'utility-operand-504304-u4','gcloud_installed':False,'authenticated':False})}],'isError':False}})+'\n'
  with patch.object(m.subprocess,'run',return_value=R()) as subprocess_run:
   d=m.call('utility_operand','gcp_status')
   self.assertTrue(d['executed'])
   self.assertEqual(subprocess_run.call_args.kwargs['env']['SOL_GCP_PROJECT_ID'],'utility-operand-504304-u4')
 def test_stdio_on_each_alias(self):
  for alias in ('utility_operand','alert_tiger'):
   r=subprocess.run([sys.executable,str(P/'gcp_dual_project.py'),'--alias',alias],capture_output=True,text=True,timeout=8)
   self.assertEqual(r.returncode,0,r.stderr)
   d=json.loads(r.stdout)
   self.assertEqual(d['alias'],alias)
   self.assertEqual(d['response']['project'],m.bindings()[alias]['project_id'])
if __name__=='__main__':unittest.main()
