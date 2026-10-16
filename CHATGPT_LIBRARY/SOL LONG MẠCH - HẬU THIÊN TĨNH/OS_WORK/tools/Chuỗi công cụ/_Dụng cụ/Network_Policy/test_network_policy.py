"""Offline unit tests only: DNS and TCP are mocked, no real network use."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import network_policy as np
import network_policy_cli as cli


class PolicyTests(unittest.TestCase):
    def make(self, obj):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        path = Path(d.name) / "policy.json"
        path.write_text(json.dumps(obj), encoding="utf-8")
        return np.load_policy(path)

    def test_default_deny_no_dns(self):
        p = np.load_policy(None)
        self.assertEqual(np.evaluate("10.15.224.21", p)["decision"], "blocked")
        with patch.object(np.socket, "getaddrinfo", side_effect=AssertionError("DNS not expected")):
            self.assertEqual(np.evaluate("example.com", p)["reason"], "default_deny")
        self.assertFalse(np.summary(p)["configured"])

    def test_allowed_ip_and_denied_by_priority(self):
        p = self.make({"always_allow": {"ip_cidrs": ["10.15.224.21/32"]}})
        self.assertEqual(np.evaluate("10.15.224.21", p)["decision"], "allowed")
        p = self.make({"always_allow": {"ip_cidrs": ["10.15.224.0/24"]},
                       "block": {"ip_cidrs": ["10.15.224.21/32"]}})
        self.assertEqual(np.evaluate("10.15.224.21", p)["reason"], "block_precedence_conflict")

    def test_wildcard_dns_allowed_and_resolved(self):
        p = self.make({"always_allow": {"dns": ["*.example.com"]}})
        with patch.object(np, "resolve_host", return_value=["203.0.113.20"]):
            self.assertEqual(np.evaluate("api.example.com", p)["decision"], "allowed")
            self.assertEqual(np.evaluate("example.com", p)["decision"], "blocked")

    def test_dns_block_never_resolves(self):
        p = self.make({"always_allow": {"dns": ["*.example.com"]},
                       "block": {"dns": ["bad.example.com"]}})
        with patch.object(np, "resolve_host", side_effect=AssertionError("must not resolve")):
            self.assertEqual(np.evaluate("bad.example.com", p)["decision"], "blocked")

    def test_dns_allowed_but_ip_blocked(self):
        p = self.make({"always_allow": {"dns": ["api.example.com"]},
                       "block": {"ip_cidrs": ["127.0.0.0/8"]}})
        with patch.object(np, "resolve_host", return_value=["127.0.0.1"]):
            self.assertEqual(np.evaluate("api.example.com", p)["reason"], "block_precedence_conflict")

    def test_bad_policy_rejected(self):
        for doc in ({"default_action": "allow"}, {"version": 2},
                    {"always_allow": {"dns": ["*.com"]}},
                    {"block": {"ip_cidrs": ["bad/net"]}}):
            with self.subTest(doc=doc), self.assertRaises(np.NetworkPolicyError):
                self.make(doc)

    def test_host_validation(self):
        for host in ("https://example.com", "bad/path", "a b", "", "host:443"):
            with self.subTest(host=host), self.assertRaises(np.NetworkPolicyError):
                np.canonical_host(host)

    def test_connect_default_deny_no_socket(self):
        with patch.object(np.socket, "create_connection", side_effect=AssertionError("no TCP")):
            with self.assertRaises(PermissionError):
                np.connect("10.15.224.21", 443, 2, np.load_policy(None))

    def test_connect_allowed_with_socket_mock(self):
        p = self.make({"always_allow": {"ip_cidrs": ["10.15.224.21/32"]}})
        class FakeSocket:
            def __enter__(self): return self
            def __exit__(self, *args): return False
        with patch.object(np.socket, "create_connection", return_value=FakeSocket()) as call:
            result = np.connect("10.15.224.21", 443, 2, p)
            self.assertTrue(result["connected"])
            call.assert_called_once_with(("10.15.224.21", 443), timeout=2)

    def test_cli_denies_without_explicit_policy_and_execute(self):
        self.assertEqual(cli.main(["connect", "10.15.224.21", "443", "--execute"]), 2)
        self.assertEqual(cli.main(["evaluate", "10.15.224.21"]), 0)


if __name__ == "__main__":
    unittest.main()
