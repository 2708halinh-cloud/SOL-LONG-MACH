"""Read-only ADB transport and Android SensorService availability probe.

Only sanitized metadata is returned. Battery values and sensor event payloads
are intentionally never persisted. SensorService availability does not prove
that a live sensor event stream has been observed.
"""
from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone

DEFAULT_TARGETS = (
    ("XIAOMI12_USB", "1056285"),
    ("REDMI_NOTE14PRO_WIRELESS", "192.168.1.14:5556"),
)
SENSOR_NAME_ALLOWLIST = (
    "LSM6DSO",
    "AK099",
    "TMD3719",
    "Accelerometer",
    "Gyroscope",
    "Magnetometer",
    "Light Sensor",
)


def probe_live_devices(adb_path: str, targets=DEFAULT_TARGETS, run=None) -> dict:
    """Probe configured ADB targets without reading or storing sensor values."""
    runner = run or subprocess.run
    result = {
        "schema": "GGDV_LIVE_DEVICE_PROBE/1.0",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z"),
        "status": "NOT_PROBED",
        "adb_binary_present": os.path.isfile(adb_path),
        "adb_devices_command_succeeded": False,
        "targets": [],
        "live_sensor_reading_confirmed": False,
    }
    if not result["adb_binary_present"]:
        result["status"] = "ADB_BINARY_MISSING"
        return result

    try:
        devices = runner([adb_path, "devices", "-l"], capture_output=True, text=True, timeout=5)
    except subprocess.TimeoutExpired:
        result["status"] = "ADB_DEVICES_TIMEOUT"
        return result
    except Exception as exc:
        result["status"] = "ADB_DEVICES_ERROR"
        result["error_type"] = type(exc).__name__
        return result

    result["adb_devices_command_succeeded"] = devices.returncode == 0
    if devices.returncode != 0:
        result["status"] = "ADB_DEVICES_FAILED"
        return result

    states = {}
    for line in (devices.stdout or "").splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[0] != "List":
            states[fields[0]] = fields[1]

    for role, serial in targets:
        item = {
            "role": role,
            "target": serial,
            "adb_state": states.get(serial, "NOT_LISTED"),
            "battery_probe_succeeded": False,
            "sensorservice_probe_succeeded": False,
            "sensor_names_observed": [],
            "sensorservice_output_line_count": 0,
            "live_sensor_event_stream_confirmed": False,
        }
        if item["adb_state"] == "device":
            try:
                battery = runner(
                    [adb_path, "-s", serial, "shell", "dumpsys", "battery"],
                    capture_output=True, text=True, timeout=5,
                )
                item["battery_probe_succeeded"] = battery.returncode == 0 and bool((battery.stdout or "").strip())
            except subprocess.TimeoutExpired:
                item["battery_probe_error"] = "TIMEOUT"
            except Exception as exc:
                item["battery_probe_error"] = type(exc).__name__

            try:
                sensors = runner(
                    [adb_path, "-s", serial, "shell", "dumpsys", "sensorservice"],
                    capture_output=True, text=True, timeout=8,
                )
                sensor_text = sensors.stdout or ""
                folded = sensor_text.casefold()
                item["sensorservice_probe_succeeded"] = sensors.returncode == 0
                item["sensor_names_observed"] = [
                    name for name in SENSOR_NAME_ALLOWLIST if name.casefold() in folded
                ]
                item["sensorservice_output_line_count"] = len(sensor_text.splitlines())
            except subprocess.TimeoutExpired:
                item["sensorservice_probe_error"] = "TIMEOUT"
            except Exception as exc:
                item["sensorservice_probe_error"] = type(exc).__name__
        result["targets"].append(item)

    result["status"] = "ADB_TRANSPORT_RESPONDED"
    result["live_sensor_reading_confirmed"] = False
    return result
