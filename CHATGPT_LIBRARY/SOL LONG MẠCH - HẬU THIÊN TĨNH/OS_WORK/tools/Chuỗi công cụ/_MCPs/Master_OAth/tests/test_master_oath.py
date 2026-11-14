import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PATH = Path(__file__).resolve().parents[1] / "master_oath.py"
spec = importlib.util.spec_from_file_location("master_oath", PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class MasterOAthTests(unittest.TestCase):
    def test_chatgpt_is_independent_provider(self):
        data = mod.route("chatgpt", "search_conversations", connected=True)
        self.assertEqual(data["url"], "https://chatgpt.com/")
        self.assertFalse(data["browser_session_verified"])
        self.assertTrue(data["connected_gmail_is_not_chatgpt_login"])

    def test_browser_handoff_does_not_invent_login_or_cookie(self):
        with patch.object(mod.webbrowser,"open",return_value=True) as browser:
            data = mod.browser_handoff("chatgpt",open_browser=True)
        browser.assert_called_once_with("https://chatgpt.com/")
        self.assertFalse(data["logged_in"])
        self.assertFalse(data["cookie_saved_by_master_oath"])
        self.assertTrue(data["browser_open_reported"])

    def test_custom_browser_url_cannot_embed_auth_data(self):
        for url in ["http://unsafe.test/", "https://u:p@example.test/", "https://example.test/?code=abc", "https://example.test/#token"]:
            with self.subTest(url=url), self.assertRaises(mod.AuthRouteError):
                mod.browser_target("custom",url)
        self.assertEqual(mod.browser_target("custom","https://example.test/"),"https://example.test/")

    def test_existing_hostinger_connector_is_preferred(self):
        route = mod.route("hostinger", "dns_records_list", connected=True, domain="gambbrazil.fun")
        self.assertEqual(route["next_agent"], "CALL_CONNECTED_HOSTINGER_PROVIDER")
        self.assertFalse(route["needs_browser"])
        self.assertEqual(route["params"], {"domain": "gambbrazil.fun"})

    def test_auth_browser_is_fallback_only(self):
        route = mod.route("hostinger", "dns_records_list", connected=False, domain="gambbrazil.fun")
        self.assertTrue(route["needs_browser"])
        self.assertEqual(route["endpoint"], "https://mcp.hostinger.com")

    def test_gmail_reuse_and_restricted_actions(self):
        self.assertEqual(mod.route("gmail", "get_profile", connected=True)["next_agent"], "CALL_CONNECTED_GMAIL_PROVIDER")
        with self.assertRaises(mod.AuthRouteError):
            mod.route("gmail", "send_email", connected=True)
        with self.assertRaises(mod.AuthRouteError):
            mod.route("hostinger", "dns_records_delete", connected=True, domain="gambbrazil.fun")

    def test_dns_summary_redacts_values_and_reports_private_ip(self):
        sample = [{"name":"gambbrazil", "type":"TXT", "ttl":3600, "records":[{"content":"a-secret-not-for-report"}]},
                  {"name":"ai.sol","type":"A","ttl":14400,"records":[{"content":"10.15.224.83"}]},
                  {"name":"www","type":"CNAME","ttl":300,"records":[{"content":"alias.test."}]}]
        data = mod.summarize_dns(sample, "gambbrazil.fun")
        self.assertTrue(data["values_redacted"])
        self.assertEqual(data["record_groups"], 3)
        self.assertEqual(data["records"][1]["address_class"], "private_or_special")
        self.assertNotIn("a-secret-not-for-report", json.dumps(data))
        self.assertNotIn("10.15.224.83", json.dumps(data))

    def test_mcp_token_not_in_status(self):
        out = io.StringIO()
        with patch.dict(mod.os.environ, {"MASTER_OATH_HOSTINGER_BEARER":"CANARY_SECRET_NEVER_ECHO"}), patch("sys.stdout", out):
            self.assertEqual(mod.main(["status"]), 0)
        self.assertNotIn("CANARY_SECRET_NEVER_ECHO", out.getvalue())
        self.assertTrue(json.loads(out.getvalue())["bearer_available_in_process"])

    def test_reject_hostile_domain(self):
        with self.assertRaises(mod.AuthRouteError):
            mod.route("hostinger", "dns_records_list", connected=True, domain="https://other.host/path")

    def test_denied_redirect(self):
        with self.assertRaises(mod.AuthRouteError):
            mod._DenyRedirect().redirect_request(None,None,302,"redirect",{},"https://other.test/")


if __name__ == "__main__":
    unittest.main()
