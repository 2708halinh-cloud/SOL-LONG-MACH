"""Offline tests. No DNS requests or Windows firewall mutation."""
import unittest
import system_router


class RoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = system_router.load()

    def test_light_warns(self):
        d = system_router.decide("https://chatgpt.com/c/123", "light", self.config)
        self.assertEqual(d["action"], "WARN")
        self.assertEqual(d["host"], "chatgpt.com")

    def test_severe_blocks_subdomain(self):
        d = system_router.decide("api.openai.com", "severe", self.config)
        self.assertEqual(d["action"], "BLOCK")
        self.assertEqual(d["rule"], "openai.com")

    def test_shared_ip_not_invented(self):
        d = system_router.decide("104.16.0.1", "severe", self.config)
        self.assertEqual(d["action"], "NO_MATCH")
        self.assertFalse(d["dynamic_ips_comprehensively_blocked"])

    def test_hostinger_owns_zone_not_resolver(self):
        d = system_router.decide("gambbrazil.gambbrazil.fun", "severe", self.config)
        self.assertEqual(d["action"], "NO_MATCH")
        self.assertIn("AUTHORITATIVE", d["relation"])

    def test_local_pc_ip_independent(self):
        d = system_router.decide("http://127.0.0.1:8765/api/devices", "severe", self.config)
        self.assertEqual(d["relation"], "THIS_DEVICE_LOOPBACK_ONLY")
        self.assertFalse(d["windows_host_policy_applied"])

    def test_unknown_not_swallowed(self):
        with self.assertRaises(ValueError):
            system_router.decide("openai.com", "other", self.config)


if __name__ == "__main__":
    unittest.main()