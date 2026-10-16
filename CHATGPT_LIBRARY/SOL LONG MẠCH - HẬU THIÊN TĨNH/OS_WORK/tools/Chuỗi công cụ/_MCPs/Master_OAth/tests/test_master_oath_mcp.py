import importlib.util, sys, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location("master_oath_mcp",ROOT/"master_oath_mcp.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class StdioMCPTests(unittest.TestCase):
    def test_chatgpt_handoff_is_independent_of_hostinger(self):
        r=m.dispatch("tools/call",{"name":"master_oath_browser_handoff","arguments":{"provider":"chatgpt"}})
        self.assertIn("https://chatgpt.com/",r["content"][0]["text"])
        self.assertIn('"logged_in": false',r["content"][0]["text"])

    def test_initialize_and_list(self):
        i=m.dispatch("initialize",{})
        self.assertEqual(i["serverInfo"]["name"],"Master OAth")
        names={t["name"] for t in m.dispatch("tools/list",{})["tools"]}
        self.assertIn("master_oath_hostinger_dns",names)
    def test_route_without_credentials(self):
        r=m.dispatch("tools/call",{"name":"master_oath_route","arguments":{"provider":"hostinger","operation":"dns_records_list","domain":"gambbrazil.fun","connected":True}})
        self.assertIn("CALL_CONNECTED_HOSTINGER_PROVIDER",r["content"][0]["text"])
    def test_dns_without_bearer_does_not_fake_success(self):
        from unittest.mock import patch
        with patch.dict(m.os.environ,{"MASTER_OATH_HOSTINGER_BEARER":""}):
            with self.assertRaises(m.AuthRouteError):
                m.dispatch("tools/call",{"name":"master_oath_hostinger_dns","arguments":{"domain":"gambbrazil.fun"}})
if __name__=="__main__":unittest.main()
