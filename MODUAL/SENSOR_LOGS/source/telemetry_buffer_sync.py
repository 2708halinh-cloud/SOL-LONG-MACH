"""
TELEMETRY BUFFER & SNAPSHOT SYNC DAEMON
MÃ BẢO TOÀN SỰ THẬT: 075203003486_10152484_20260724124936
QUY TẮC CỐT LÕI: 0000_THE_MASTER_TEACHER.md - HÀ LINH (LÃNH ĐẠO)
SLOGAN: NO ELIMINATION — NO COMPETITION — NO SERVICE

CHỨC NĂNG:
1. Thu thập thông số từ:
   - Máy tính Windows (CPU, RAM, Disks, Network, Mesh Ports, Local AI Ollama, DeskIn)
   - Xiaomi 12 (Live USB ADB: Battery, Temp, Voltage, Sensors)
   - Redmi Note 14 Pro 5G (Specs, Cache, CrossDevice Storage)
2. Ghi liên tục (append) vào vùng đệm cục bộ SSD tốc độ cao:
   Thư mục cảm biến được kiểm từ vật mang hiện có, ưu tiên C:\\Dropbox\\SESON_LOGS\\_SESORIMOTOR__WINDOWS__XIAOMI12__REDMINOTE14PRO__0000THEMASTERTEACHER__R000_075203003486__.CSV
3. Tự động đồng bộ định kỳ (Snapshot Atomic Write) sang Google Drive:
   W:\\Drive của tôi\\.vscode\\thiẾT bỊ\\Thành Lập 6 viên ĐÁ VÔ CỰC - The Creation of the 6 Infinity Stones\\_SESORIMOTOR__WINDOWS__XIAOMI12__REDMINOTE14PRO__0000THEMASTERTEACHER__R000_075203003486__.CSV
   -> Khắc phục triệt để lỗi xung đột file lock, crash ổ W: và lỗi tự xóa file vào thùng rác.
"""

import os
import sys
import time
import csv
import shutil
import datetime
import subprocess
import hashlib
import json
from pathlib import Path

try:
    from .sensor_root_resolver import inspect_sources
except ImportError:  # direct script invocation
    from sensor_root_resolver import inspect_sources

# Pin this consumer to the provider-verified materialization. Fail closed; never auto-select another CSV.
os.environ["SOL_SENSOR_SOURCE_FILE"] = r"D:\SENSOR_LOGS\windows_SENSON.CSV"
_source_observation = inspect_sources()
if not _source_observation["source_verified"] or not _source_observation.get("selected_evidence"):
    raise FileNotFoundError("NO_SENSOR_CSV_BYTES_VERIFIED; no synthetic file is created")
BUFFER_CSV = _source_observation["selected_evidence"]["file"]
BUFFER_DIR = str(Path(BUFFER_CSV).parent)

TARGET_CSV = r"w:\Drive của tôi\.vscode (1)\thiẾT bỊ\Thành Lập 6 viên ĐÁ VÔ CỰC - The Creation of the 6 Infinity Stones\_SESORIMOTOR__WINDOWS__XIAOMI12__REDMINOTE14PRO__0000THEMASTERTEACHER__R000_075203003486__.CSV"
ADB_PATH = r"C:\Users\halin\platform-tools-latest-windows\platform-tools\adb.exe"
MODUAL_GITHUB_SYNC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modual_github_sync.py")


def get_xiaomi_telemetry():
    telemetry = {
        "model": "2201123G (Cupid Global)",
        "os": "Android 15 (HyperOS OS3.0.4.0.VLCMIXM)",
        "soc": "Snapdragon 8 Gen 1 (SM8450 / taro)",
        "cpu": "ARMv9-A (1x Cortex-X2 3.0GHz + 3x Cortex-A710 2.5GHz + 4x Cortex-A510 1.8GHz)",
        "gpu": "Qualcomm Adreno 730",
        "ram_gb": "8",
        "battery_pct": "100",
        "battery_temp_c": "34.7",
        "battery_voltage_mv": "4380",
        "battery_status": "Full",
        "usb_powered": "True",
        "active_sensors_count": "2",
        "lsm6dso_accel": "Online / Calibrated",
        "lsm6dso_gyro": "Online / Calibrated",
        "ak0991x_mag": "Online",
        "tmd3719_light": "Online",
        "transport": "USB_ADB_PHYSICAL_LIVE"
    }
    try:
        res = subprocess.run([ADB_PATH, "-s", "1056285", "shell", "dumpsys battery"], capture_output=True, text=True, timeout=3)
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                line = line.strip()
                if line.startswith("level:"):
                    telemetry["battery_pct"] = line.split(":", 1)[1].strip()
                elif line.startswith("voltage:"):
                    telemetry["battery_voltage_mv"] = line.split(":", 1)[1].strip()
                elif line.startswith("temperature:"):
                    temp_raw = float(line.split(":", 1)[1].strip())
                    telemetry["battery_temp_c"] = f"{temp_raw / 10.0:.1f}"
                elif line.startswith("status:"):
                    st = line.split(":", 1)[1].strip()
                    telemetry["battery_status"] = "Full" if st == "5" else "Charging" if st == "2" else f"Code_{st}"
                elif line.startswith("USB powered:"):
                    telemetry["usb_powered"] = line.split(":", 1)[1].strip()
    except Exception:
        pass
    return telemetry

def get_redmi_telemetry():
    return {
        "model": "24090RA29G",
        "os": "HyperOS (Android 14/15)",
        "soc": "MediaTek Dimensity 7300-Ultra / Snapdragon 7s Gen 2",
        "cpu": "ARMv8/v9 (4x A78 2.5GHz + 4x A55 2.0GHz)",
        "gpu": "Mali-G615 MC2",
        "ram_gb": "8/12",
        "storage_gb": "256/512",
        "battery_mah": "5500",
        "charging_w": "45W/67W",
        "display": "1.5K 120Hz Curved AMOLED",
        "camera_mp": "50MP/200MP OIS",
        "sensors": "Accel, Gyro, Compass, Light, Virtual Proximity, In-display Fingerprint",
        "crossdevice_path": r"C:\Users\halin\CrossDevice\Redmi Note 14 Pro 5G",
        "wireless_adb": "192.168.1.14:5556 (Profile Cached / Standby)"
    }

def get_pc_telemetry():
    return {
        "hostname": "DESKTOP-86ITNQ4",
        "os": "Windows 11 Enterprise x64 (Build 26100.3194)",
        "cpu": "Intel Core i5-10400F (6C/12T, AVX2, FMA3)",
        "ram_total_gb": "48",
        "gpu": "NVIDIA GeForce GT 1030 (2GB GDDR5)",
        "deskin_id": "677 075 397",
        "deskin_status": "Ready / Online",
        "ollama_endpoint": "http://127.0.0.1:11434",
        "ollama_models": r"D:\AI_LOCAL\ollama\models",
        "port_minh": "8765",
        "port_sol": "8766",
        "port_mei": "8767",
        "port_cockpit": "8770",
        "storage_c": "C:\\ (NVMe SSD)",
        "storage_d": "D:\\ (AI & Data NVMe SSD)",
        "storage_g": "G:\\ (Backup HDD)",
        "storage_w": "W:\\Drive của tôi (Google Drive File Stream)",
        "sync_mechanism": "LOCAL_BUFFER_SAFE_SNAPSHOT_SYNC",
        "provenance_code": "075203003486_10152484_20260724124936",
        "canonical_rule": "0000_THE_MASTER_TEACHER.md"
    }

def sync_snapshot_to_cloud():
    # NEVER send private sensor bytes or replace an existing cloud carrier by
    # default. Separate explicit export requires a reviewed target.
    if os.getenv("SOL_ENABLE_SENSOR_CLOUD_EXPORT", "").strip() != "1":
        return False
    try:
        if not os.path.exists(BUFFER_CSV):
            return False

        target_dir = os.path.dirname(TARGET_CSV)
        os.makedirs(target_dir, exist_ok=True)

        temp_target = TARGET_CSV + ".tmp_sync"
        if os.path.exists(temp_target):
            os.remove(temp_target)

        source_size_before = os.path.getsize(BUFFER_CSV)
        shutil.copyfile(BUFFER_CSV, temp_target)

        if not os.path.exists(temp_target):
            raise RuntimeError("TMP_SYNC_MISSING_AFTER_COPY")

        temp_size = os.path.getsize(temp_target)
        source_size_after = os.path.getsize(BUFFER_CSV)
        if not (source_size_before <= temp_size <= source_size_after):
            raise RuntimeError(
                f"TMP_SYNC_RANGE_MISMATCH before={source_size_before} temp={temp_size} after={source_size_after}"
            )

        os.replace(temp_target, TARGET_CSV)

        if not os.path.exists(TARGET_CSV):
            raise RuntimeError("TARGET_MISSING_AFTER_REPLACE")
        if os.path.getsize(TARGET_CSV) != temp_size:
            raise RuntimeError("TARGET_SIZE_MISMATCH")

        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Snapshot synchronized to Google Drive safely.")
        return True
    except Exception as e:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Sync notice: {e}")
        return False

def sync_snapshot_to_github():
    # GitHub snapshot may commit/push source-derived metadata and latest rows.
    # It must not run merely because this reader started.
    if os.getenv("SOL_ENABLE_SENSOR_GITHUB_PUSH", "").strip() != "1":
        return False
    try:
        if not os.path.exists(MODUAL_GITHUB_SYNC):
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] GitHub sync helper missing: {MODUAL_GITHUB_SYNC}")
            return False
        res = subprocess.run(
            [sys.executable, MODUAL_GITHUB_SYNC],
            capture_output=True,
            text=True,
            timeout=240,
        )
        if res.returncode != 0:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] GitHub MODUAL sync failed: {res.stderr[-2000:]}")
            return False
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] GitHub MODUAL state synchronized.")
        return True
    except Exception as e:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] GitHub sync notice: {e}")
        return False

def record_telemetry_tick():
    """Read a real sensor carrier; never manufacture readings or append to it.

    This is a read-only sample: byte count, SHA-256 and modification time.
    A genuine HWiNFO live sample requires a separate before/after observation.
    """
    source = Path(BUFFER_CSV)
    before = source.stat()
    if before.st_size < 12:
        raise ValueError("SOURCE_FILE_TOO_SMALL")
    digest = hashlib.sha256()
    with source.open("rb") as fd:
        for block in iter(lambda: fd.read(1024 * 1024), b""):
            digest.update(block)
    after = source.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError("SOURCE_CHANGED_DURING_READ_RETRY_LATER")
    result = {
        "source": str(source),
        "bytes": before.st_size,
        "modified_ns": before.st_mtime_ns,
        "sha256": digest.hexdigest(),
        "source_file_written": False,
        "synthetic_rows_added": 0,
        "live_sensor_reading_confirmed": False,
    }
    print(f"SOURCE_OBSERVED bytes={result['bytes']} sha256={result['sha256']}")
    return result


def write_tick_receipt(result: dict, mode: str) -> dict:
    """Persist a unique metadata-only receipt; never copy sensor rows."""
    observed_at = datetime.datetime.now(datetime.timezone.utc)
    receipt = {
        "schema": "GGDV_WINDOWS_TICK_RECEIPT/1.0",
        "observed_at_utc": observed_at.isoformat(timespec="microseconds").replace("+00:00", "Z"),
        "mode": mode,
        "source": {
            "path": result["source"],
            "bytes": result["bytes"],
            "modified_ns": result["modified_ns"],
            "sha256": result["sha256"],
        },
        "mutations": {
            "source_file_written": False,
            "synthetic_rows_added": 0,
        },
        "live_sensor_reading_confirmed": False,
        "exports": {
            "cloud_enabled": os.getenv("SOL_ENABLE_SENSOR_CLOUD_EXPORT", "").strip() == "1",
            "github_enabled": os.getenv("SOL_ENABLE_SENSOR_GITHUB_PUSH", "").strip() == "1",
        },
    }
    receipt_dir = Path(__file__).resolve().parent / "state"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    filename = "WINDOWS_TICK_" + observed_at.strftime("%Y%m%dT%H%M%S%fZ") + ".json"
    target = receipt_dir / filename
    encoded = json.dumps(receipt, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\\n"
    with target.open("x", encoding="utf-8", newline="\\n") as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())
    readback = target.read_text(encoding="utf-8")
    if readback != encoded:
        raise RuntimeError("TICK_RECEIPT_EXACT_READBACK_FAILED")
    digest = hashlib.sha256(readback.encode("utf-8")).hexdigest()
    print(f"TICK_RECEIPT path={target} bytes={len(readback.encode('utf-8'))} sha256={digest} readback_ok=true")
    return {"path": str(target), "bytes": len(readback.encode("utf-8")), "sha256": digest}


def main():
    print("=" * 60)
    print("TELEMETRY BUFFER & SNAPSHOT SYNC DAEMON ACTIVE")
    print(f"Local Buffer: {BUFFER_CSV}")
    print(f"Cloud Target: {TARGET_CSV}")
    print("Provenance Code: 075203003486_10152484_20260724124936")
    print("=" * 60)

    # Initial sync
    sync_snapshot_to_cloud()
    sync_snapshot_to_github()

    tick_count = 0
    while True:
        try:
            write_tick_receipt(record_telemetry_tick(), mode="loop")
            tick_count += 1
            # Every 10 ticks (~5 minutes if sleep 30s), trigger cloud snapshot
            if tick_count % 10 == 0:
                sync_snapshot_to_cloud()
                sync_snapshot_to_github()
        except KeyboardInterrupt:
            print("\nDaemon stopping gracefully...")
            sync_snapshot_to_cloud()
            sync_snapshot_to_github()
            break
        except Exception as e:
            print(f"Tick error: {e}")
        time.sleep(30)

if __name__ == "__main__":
    args = sys.argv[1:]
    # Task Scheduler defaults to one finite observation; daemon mode is opt-in.
    if args in ([], ["--once"]):
        write_tick_receipt(record_telemetry_tick(), mode="once")
        sync_snapshot_to_cloud()
        sync_snapshot_to_github()
        print("Completed one-shot sensor observation; export requires explicit enable flags.")
    elif args == ["--loop"]:
        main()
    else:
        raise SystemExit("Usage: telemetry_buffer_sync.py [--once|--loop]")
