"""Read-only ADB transport and live SensorService event-timestamp probe.

Only sanitized metadata is returned. Battery values and sensor event payloads
are intentionally never persisted. A live stream is confirmed only when an
allowlisted sensor's monotonic event timestamp advances between two snapshots.
"""
from __future__ import annotations

import os
import re
import subprocess
import time
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

_EVENT_HEADER_PATTERNS = (
    ("LSM6DSO_ACCELEROMETER", re.compile(r"\blsm6dso\b.*\baccelerometer\b.*:\s*last\s+\d+\s+events", re.I)),
    ("LSM6DSO_GYROSCOPE", re.compile(r"\blsm6dso\b.*\bgyroscope\b.*:\s*last\s+\d+\s+events", re.I)),
    ("AK099_MAGNETOMETER", re.compile(r"\bak099\w*\b.*\bmagnetometer\b.*:\s*last\s+\d+\s+events", re.I)),
    ("TMD3719_LIGHT", re.compile(r"\btmd3719\w*\b.*(?:ambient light|light sensor).*:\s*last\s+\d+\s+events", re.I)),
    ("ACCELEROMETER", re.compile(r"\baccelerometer\b.*:\s*last\s+\d+\s+events", re.I)),
    ("GYROSCOPE", re.compile(r"\bgyroscope\b.*:\s*last\s+\d+\s+events", re.I)),
    ("MAGNETOMETER", re.compile(r"\bmagnetometer\b.*:\s*last\s+\d+\s+events", re.I)),
    ("LIGHT_SENSOR", re.compile(r"\blight sensor\b.*:\s*last\s+\d+\s+events", re.I)),
)
_EVENT_TIMESTAMP = re.compile(r"\bts=([0-9]+(?:\.[0-9]+)?)")


def _latest_allowlisted_event_timestamps(sensor_text: str) -> dict[str, float]:
    """Return only latest monotonic timestamps for allowlisted sensor headers."""
    in_recent_events = False
    current_sensor = None
    latest: dict[str, float] = {}

    for line in sensor_text.splitlines():
        if "Recent Sensor events" in line:
            in_recent_events = True
            continue
        if in_recent_events and line.strip().startswith("Active sensors:"):
            break
        if not in_recent_events:
            continue

        if re.search(r":\s*last\s+\d+\s+events", line, re.I):
            current_sensor = next(
                (name for name, pattern in _EVENT_HEADER_PATTERNS if pattern.search(line)),
                None,
            )
            continue

        if current_sensor is None:
            continue
        match = _EVENT_TIMESTAMP.search(line)
        if match:
            value = float(match.group(1))
            latest[current_sensor] = max(latest.get(current_sensor, -1.0), value)

    return latest


def probe_live_devices(
    adb_path: str,
    targets=DEFAULT_TARGETS,
    run=None,
    sleep_fn=None,
    sample_interval_seconds: float = 2.0,
) -> dict:
    """Probe configured ADB targets without returning sensor or battery values."""
    runner = run or subprocess.run
    sleeper = sleep_fn or time.sleep
    result = {
        "schema": "GGDV_LIVE_DEVICE_PROBE/1.1",
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
            "sensor_event_stream_probe_interval_seconds": sample_interval_seconds,
            "sensor_event_timestamp_sensor_count": 0,
            "sensor_event_sensors_advanced": [],
            "sensor_event_stream_status": "NOT_PROBED",
            "live_sensor_event_stream_confirmed": False,
        }
        if item["adb_state"] == "device":
            try:
                battery = runner(
                    [adb_path, "-s", serial, "shell", "dumpsys", "battery"],
                    capture_output=True, text=True, timeout=5,
                )
                item["battery_probe_succeeded"] = (
                    battery.returncode == 0 and bool((battery.stdout or "").strip())
                )
            except subprocess.TimeoutExpired:
                item["battery_probe_error"] = "TIMEOUT"
            except Exception as exc:
                item["battery_probe_error"] = type(exc).__name__

            try:
                first = runner(
                    [adb_path, "-s", serial, "shell", "dumpsys", "sensorservice"],
                    capture_output=True, text=True, timeout=8,
                )
                if first.returncode != 0:
                    item["sensorservice_probe_error"] = "FIRST_SNAPSHOT_FAILED"
                else:
                    first_text = first.stdout or ""
                    try:
                        sleeper(max(0.0, sample_interval_seconds))
                        second = runner(
                            [adb_path, "-s", serial, "shell", "dumpsys", "sensorservice"],
                            capture_output=True, text=True, timeout=8,
                        )
                        if second.returncode != 0:
                            item["sensorservice_probe_error"] = "SECOND_SNAPSHOT_FAILED"
                        else:
                            sensor_text = second.stdout or ""
                            first_events = _latest_allowlisted_event_timestamps(first_text)
                            second_events = _latest_allowlisted_event_timestamps(sensor_text)
                            common = set(first_events).intersection(second_events)
                            advanced = sorted(
                                name for name in common
                                if second_events[name] > first_events[name]
                            )
                            item["sensorservice_probe_succeeded"] = True
                            item["sensor_names_observed"] = [
                                name for name in SENSOR_NAME_ALLOWLIST
                                if name.casefold() in sensor_text.casefold()
                            ]
                            item["sensorservice_output_line_count"] = len(sensor_text.splitlines())
                            item["sensor_event_timestamp_sensor_count"] = len(second_events)
                            item["sensor_event_sensors_advanced"] = advanced
                            item["live_sensor_event_stream_confirmed"] = bool(advanced)
                            if advanced:
                                item["sensor_event_stream_status"] = "EVENT_TIMESTAMP_ADVANCED"
                            elif common:
                                item["sensor_event_stream_status"] = "EVENT_TIMESTAMP_STALE"
                            else:
                                item["sensor_event_stream_status"] = "EVENT_TIMESTAMPS_INSUFFICIENT"
                    except subprocess.TimeoutExpired:
                        item["sensorservice_probe_error"] = "SECOND_SNAPSHOT_TIMEOUT"
            except subprocess.TimeoutExpired:
                item["sensorservice_probe_error"] = "FIRST_SNAPSHOT_TIMEOUT"
            except Exception as exc:
                item["sensorservice_probe_error"] = type(exc).__name__
        result["targets"].append(item)

    result["status"] = "ADB_TRANSPORT_RESPONDED"
    result["live_sensor_reading_confirmed"] = any(
        target["live_sensor_event_stream_confirmed"] for target in result["targets"]
    )
    return result
