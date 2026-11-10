#!/usr/bin/env python3
"""Regression tests for resource-aware SSH/VNC routing. Does not start GUI."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
import ssh_vnc_router as router


class RouterTests(unittest.TestCase):
    def test_route_read_is_side_effect_free(self):
        with patch.object(router, "start_vnc", side_effect=AssertionError("VNC_STARTED")):
            with patch.object(router, "start_ssh", side_effect=AssertionError("SSH_STARTED")):
                result = router.plan("read", activate=True)
        self.assertEqual(result["route"], "DESKTOP_COMMANDER_FILE_READ")
        self.assertFalse(result["requires_vnc"])

    def test_shell_plan_does_not_start_gui(self):
        with patch.object(router, "start_vnc", side_effect=AssertionError("VNC_STARTED")):
            result = router.plan("shell")
        self.assertEqual(result["route"], "SSH_COMMAND_ONLY")
        self.assertFalse(result["observed"]["vnc"]["localhost_open"])

    def test_gui_without_activation_does_not_start(self):
        with patch.object(router, "start_vnc", side_effect=AssertionError("VNC_STARTED")):
            result = router.plan("gui", activate=False)
        self.assertTrue(result["requires_vnc"])
        self.assertFalse(result["observed"]["vnc"]["localhost_open"])

    def test_invalid_route(self):
        with self.assertRaises(ValueError):
            router.plan("format")

    def test_reject_public_bind(self):
        with self.assertRaises(ValueError):
            router.valid_bind("8.8.8.8")

    def test_reject_external_loopback_alias(self):
        with self.assertRaises(ValueError):
            router.valid_bind("127.0.0.2")

    def test_accept_localhost(self):
        self.assertEqual(router.valid_bind("127.0.0.1"), "127.0.0.1")

    def test_non_router_vnc_stop_fails_safe(self):
        with patch.object(router, "STATE", Path("/tmp/sol_router_no_owner_test__no_vnc")):
            result = router.stop_vnc()
        self.assertEqual(result["status"], "NOT_ROUTER_OWNED")
        self.assertFalse(result["stopped"])

    def test_ssh_key_only_config(self):
        cfg = (router.STATE / "router_sshd.conf").read_text()
        self.assertIn("PasswordAuthentication no", cfg)
        self.assertIn("AuthenticationMethods publickey", cfg)
        self.assertIn("ListenAddress 127.0.0.1", cfg)
        self.assertIn("AllowTcpForwarding local", cfg)

    def test_ssh_real_authentication(self):
        result = router.probe_ssh("127.0.0.1")
        self.assertTrue(result["ssh_authenticated"])
        self.assertEqual(result["exit_code"], 0)

    def test_vnc_is_idle_after_smoke_test(self):
        self.assertFalse(router.status()["vnc"]["localhost_open"])

    def test_no_sensitive_values_in_status(self):
        body=json.dumps(router.status())
        self.assertNotIn("PRIVATE KEY", body)
        self.assertNotIn("password=", body)


if __name__ == "__main__":
    unittest.main(verbosity=2)