import importlib.util, json, pathlib, subprocess, sys, unittest
SERVER = pathlib.Path(__file__).resolve().parents[1]/'google_cloud_mcp.py'
spec = importlib.util.spec_from_file_location('google_cloud_mcp', SERVER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class MCPTests(unittest.TestCase):
    def test_initialize(self):
        result=module.handle({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18'}})
        self.assertEqual(result['result']['serverInfo']['name'],'Google Cloud')
    def test_list_tools(self):
        result=module.handle({'jsonrpc':'2.0','id':2,'method':'tools/list'})
        self.assertEqual(len(result['result']['tools']),8)
        self.assertEqual(len({x['name'] for x in result['result']['tools']}),8)
    def test_gcp_usage_analyse_offline(self):
        from unittest.mock import patch
        metrics = [
            {"api":"Compute Engine API","requests":49,"error_percent":100},
            {"api":"Cloud Storage API","requests":4,"error_percent":100},
            {"api":"App Hub API","requests":15,"error_percent":0},
        ]
        with patch.object(module, "execute_gcloud", side_effect=AssertionError("PROVIDER_CALL_FORBIDDEN")):
            response = module.handle({"jsonrpc":"2.0","id":9,"method":"tools/call",
                "params":{"name":"gcp_usage_analyse","arguments":{"metrics":metrics}}})
        self.assertFalse(response["result"]["isError"])
        report = json.loads(response["result"]["content"][0]["text"])
        self.assertEqual(report["estimated_failed_requests"], 53)
        self.assertEqual(report["known_requests"], 68)
        self.assertEqual(report["provider_api_calls"], 0)
        self.assertEqual(report["cost"], "UNKNOWN_REQUIRES_BILLING_EVIDENCE")
    def test_usage_guard_rejects_arbitrary_command(self):
        response = module.handle({"jsonrpc":"2.0","id":10,"method":"tools/call",
           "params":{"name":"gcp_usage_analyse","arguments":{"command":"gcloud compute instances list"}}})
        self.assertTrue(response["result"]["isError"])
    def test_ping(self):
        self.assertEqual(module.handle({'jsonrpc':'2.0','id':3,'method':'ping'})['result'],{})
    def test_no_arbitrary_commands(self):
        result=module.handle({'jsonrpc':'2.0','id':4,'method':'tools/call','params':{'name':'gcp_run_arbitrary','arguments':{'command':'rm'}}})
        self.assertTrue(result['result']['isError'])
    def test_error_when_no_gcloud(self):
        import unittest.mock
        with unittest.mock.patch.object(module.shutil,'which',return_value=None):
            value=module.dispatch('gcp_status',{})
            self.assertFalse(value['gcloud_installed'])
    def test_stdio_handshake(self):
        reqs='\n'.join([json.dumps({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18'}}),json.dumps({'jsonrpc':'2.0','id':2,'method':'tools/list'})])+'\n'
        p=subprocess.run([sys.executable,str(SERVER)],input=reqs,text=True,capture_output=True,timeout=5)
        self.assertEqual(p.returncode,0)
        messages=[json.loads(row) for row in p.stdout.strip().splitlines()]
        self.assertEqual([m['id'] for m in messages],[1,2])
        self.assertFalse(p.stderr)

if __name__=='__main__': unittest.main()
