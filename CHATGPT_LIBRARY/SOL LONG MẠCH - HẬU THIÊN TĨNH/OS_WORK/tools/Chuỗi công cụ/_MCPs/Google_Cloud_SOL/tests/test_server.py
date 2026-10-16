import importlib.util, json, pathlib, subprocess, sys, unittest
SERVER = pathlib.Path(__file__).resolve().parents[1]/'tools/google_cloud/server.py'
spec = importlib.util.spec_from_file_location('google_cloud_mcp', SERVER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class MCPTests(unittest.TestCase):
    def test_initialize(self):
        result=module.handle({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18'}})
        self.assertEqual(result['result']['serverInfo']['name'],'Google Cloud')
    def test_list_tools(self):
        result=module.handle({'jsonrpc':'2.0','id':2,'method':'tools/list'})
        self.assertEqual(len(result['result']['tools']),7)
        self.assertEqual(len({x['name'] for x in result['result']['tools']}),7)
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
