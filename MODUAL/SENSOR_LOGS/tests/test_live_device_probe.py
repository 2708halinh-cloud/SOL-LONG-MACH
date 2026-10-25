"""Sanitized live-device probe tests; no device or source sensor bytes required."""
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

SOURCE = Path(__file__).resolve().parents[1] / "source"
import sys
sys.path.insert(0, str(SOURCE))
from live_device_probe import probe_live_devices


class LiveDeviceProbeTests(unittest.TestCase):
    def test_connected_device_reports_availability_without_raw_values(self):
        calls = []

        def fake_run(args, **kwargs):
            calls.append(args)
            if args[1:] == ["devices", "-l"]:
                return SimpleNamespace(
                    returncode=0,
                    stdout=(
                        "List of devices attached\n"
                        "1056285 device product:cupid_global model:2201123G\n"
                        "192.168.1.14:5556 offline\n"
                    ),
                    stderr="",
                )
            if args[-1] == "battery":
                return SimpleNamespace(returncode=0, stdout="level: 100\nvoltage: 4396\n", stderr="")
            if args[-1] == "sensorservice":
                return SimpleNamespace(
                    returncode=0,
                    stdout="Sensor List:\nLSM6DSO Accelerometer\nAK099 Magnetometer\nTMD3719 Light Sensor\n",
                    stderr="",
                )
            raise AssertionError("unexpected command")

        with tempfile.TemporaryDirectory() as directory:
            adb = Path(directory) / "adb.exe"
            adb.write_bytes(b"test fixture only")
            result = probe_live_devices(str(adb), run=fake_run)

        self.assertEqual(result["status"], "ADB_TRANSPORT_RESPONDED")
        self.assertFalse(result["live_sensor_reading_confirmed"])
        xiaomi, redmi = result["targets"]
        self.assertEqual(xiaomi["adb_state"], "device")
        self.assertTrue(xiaomi["battery_probe_succeeded"])
        self.assertTrue(xiaomi["sensorservice_probe_succeeded"])
        self.assertEqual(xiaomi["sensor_names_observed"], ["LSM6DSO", "AK099", "TMD3719"])
        self.assertEqual(redmi["adb_state"], "offline")
        self.assertFalse(redmi["battery_probe_succeeded"])
        self.assertFalse(redmi["sensorservice_probe_succeeded"])
        serialized = json.dumps(result)
        self.assertNotIn("4396", serialized)
        self.assertNotIn("level: 100", serialized)
        self.assertEqual(len(calls), 3)

    def test_unlisted_device_is_not_probed(self):
        def fake_run(args, **kwargs):
            return SimpleNamespace(returncode=0, stdout="List of devices attached\n", stderr="")

        with tempfile.TemporaryDirectory() as directory:
            adb = Path(directory) / "adb.exe"
            adb.write_bytes(b"test fixture only")
            result = probe_live_devices(str(adb), targets=(("TEST", "test-serial"),), run=fake_run)

        self.assertEqual(result["targets"][0]["adb_state"], "NOT_LISTED")
        self.assertEqual(result["status"], "ADB_TRANSPORT_RESPONDED")
        self.assertFalse(result["live_sensor_reading_confirmed"])

    def test_adb_timeout_is_explicit_and_nonfatal(self):
        def fake_run(args, **kwargs):
            raise subprocess.TimeoutExpired(args, timeout=5)

        with tempfile.TemporaryDirectory() as directory:
            adb = Path(directory) / "adb.exe"
            adb.write_bytes(b"test fixture only")
            result = probe_live_devices(str(adb), run=fake_run)

        self.assertEqual(result["status"], "ADB_DEVICES_TIMEOUT")
        self.assertFalse(result["live_sensor_reading_confirmed"])
        self.assertEqual(result["targets"], [])


if __name__ == "__main__":
    unittest.main()
