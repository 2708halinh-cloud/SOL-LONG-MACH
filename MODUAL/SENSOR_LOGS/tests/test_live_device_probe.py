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


def sensorservice_text(timestamp: float, values: str = "0.15, 0.11, 9.80") -> str:
    return (
        "Sensor List:\n"
        "LSM6DSO Accelerometer\n"
        "AK099 Magnetometer\n"
        "TMD3719 Light Sensor\n"
        "Recent Sensor events:\n"
        "lsm6dso Accelerometer Non-wakeup: last 1 events\n"
        f"  1 (ts={timestamp:.3f}, wall=09:00:00.000) {values}\n"
        "Active sensors:\n"
        "lsm6dso Accelerometer Non-wakeup (handle=1, connections=1)\n"
        "1 active connections\n"
    )


class LiveDeviceProbeTests(unittest.TestCase):
    def _run_probe(self, sensor_snapshots, targets=None):
        calls = []
        remaining = iter(sensor_snapshots)

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
                return SimpleNamespace(
                    returncode=0,
                    stdout="level: 100\nvoltage: 4396\n",
                    stderr="",
                )
            if args[-1] == "sensorservice":
                return SimpleNamespace(returncode=0, stdout=next(remaining), stderr="")
            raise AssertionError("unexpected command")

        with tempfile.TemporaryDirectory() as directory:
            adb = Path(directory) / "adb.exe"
            adb.write_bytes(b"test fixture only")
            result = probe_live_devices(
                str(adb),
                targets=targets or (
                    ("XIAOMI12_USB", "1056285"),
                    ("REDMI_NOTE14PRO_WIRELESS", "192.168.1.14:5556"),
                ),
                run=fake_run,
                sleep_fn=lambda _: None,
                sample_interval_seconds=2.0,
            )
        return result, calls

    def test_frozen_sensorservice_is_not_misreported_as_live(self):
        frozen = sensorservice_text(100.0)
        result, calls = self._run_probe([frozen, frozen])

        self.assertEqual(result["status"], "ADB_TRANSPORT_RESPONDED")
        self.assertFalse(result["live_sensor_reading_confirmed"])
        xiaomi, redmi = result["targets"]
        self.assertEqual(xiaomi["adb_state"], "device")
        self.assertTrue(xiaomi["battery_probe_succeeded"])
        self.assertTrue(xiaomi["sensorservice_probe_succeeded"])
        self.assertEqual(xiaomi["sensor_names_observed"], [
            "LSM6DSO", "AK099", "TMD3719",
            "Accelerometer", "Magnetometer", "Light Sensor",
        ])
        self.assertEqual(xiaomi["sensor_event_stream_status"], "EVENT_TIMESTAMP_STALE")
        self.assertFalse(xiaomi["live_sensor_event_stream_confirmed"])
        self.assertEqual(redmi["adb_state"], "offline")
        self.assertFalse(redmi["battery_probe_succeeded"])
        self.assertFalse(redmi["sensorservice_probe_succeeded"])
        serialized = json.dumps(result)
        self.assertNotIn("4396", serialized)
        self.assertNotIn("level: 100", serialized)
        self.assertNotIn("0.15, 0.11, 9.80", serialized)
        self.assertEqual(len(calls), 4)

    def test_advancing_allowlisted_event_timestamp_confirms_stream(self):
        first = sensorservice_text(100.0, "0.10, 0.20, 9.70")
        second = sensorservice_text(102.0, "0.15, 0.11, 9.80")
        result, _ = self._run_probe([first, second], targets=(("XIAOMI12_USB", "1056285"),))

        self.assertTrue(result["live_sensor_reading_confirmed"])
        target = result["targets"][0]
        self.assertTrue(target["live_sensor_event_stream_confirmed"])
        self.assertEqual(target["sensor_event_stream_status"], "EVENT_TIMESTAMP_ADVANCED")
        self.assertEqual(target["sensor_event_sensors_advanced"], ["LSM6DSO_ACCELEROMETER"])
        serialized = json.dumps(result)
        self.assertNotIn("0.10, 0.20, 9.70", serialized)
        self.assertNotIn("0.15, 0.11, 9.80", serialized)

    def test_sensorservice_availability_without_event_timestamps_is_insufficient(self):
        empty = "Sensor List:\nLSM6DSO Accelerometer\nActive sensors:\n"
        result, _ = self._run_probe([empty, empty], targets=(("XIAOMI12_USB", "1056285"),))

        self.assertTrue(result["targets"][0]["sensorservice_probe_succeeded"])
        self.assertEqual(result["targets"][0]["sensor_event_stream_status"], "EVENT_TIMESTAMPS_INSUFFICIENT")
        self.assertFalse(result["live_sensor_reading_confirmed"])

    def test_unlisted_device_is_not_probed(self):
        def fake_run(args, **kwargs):
            return SimpleNamespace(returncode=0, stdout="List of devices attached\n", stderr="")

        with tempfile.TemporaryDirectory() as directory:
            adb = Path(directory) / "adb.exe"
            adb.write_bytes(b"test fixture only")
            result = probe_live_devices(
                str(adb),
                targets=(("TEST", "test-serial"),),
                run=fake_run,
                sleep_fn=lambda _: None,
            )

        self.assertEqual(result["targets"][0]["adb_state"], "NOT_LISTED")
        self.assertEqual(result["status"], "ADB_TRANSPORT_RESPONDED")
        self.assertFalse(result["live_sensor_reading_confirmed"])

    def test_adb_timeout_is_explicit_and_nonfatal(self):
        def fake_run(args, **kwargs):
            raise subprocess.TimeoutExpired(args, timeout=5)

        with tempfile.TemporaryDirectory() as directory:
            adb = Path(directory) / "adb.exe"
            adb.write_bytes(b"test fixture only")
            result = probe_live_devices(str(adb), run=fake_run, sleep_fn=lambda _: None)

        self.assertEqual(result["status"], "ADB_DEVICES_TIMEOUT")
        self.assertFalse(result["live_sensor_reading_confirmed"])
        self.assertEqual(result["targets"], [])


if __name__ == "__main__":
    unittest.main()
