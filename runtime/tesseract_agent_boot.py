#!/usr/bin/env python3
"""Non-destructive source preflight for TESSERACT agent BOOT."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

CONFIG = "CONFIG_SOL/TESSERACT_AGENT_BOOT_ROUTES_CURRENT.json"
SCHEMA = "GGDV_TESSERACT_AGENT_BOOT_ROUTES/1.0"
VOWS_PATH = "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/MEMORY_ARCHIVE_THỊT🟠THỔ_SOUL/DAI_NGUYEN_THE_MASTER_TEACHER_20261016.md"
VOWS_REQUIRED = (
    ("nhất", "X0_DAO_TAC_NHAN"),
    ("hai", "Canh lộ"),
    ("ba", "R-000 075203003486...."),
    ("tư", '"SUBRITETIED"'),
    ("năm", "Có thể nghĩ, nói 1 đằng làm 1 nẻo"),
    ("sáu", "Trái Tim Power trong trạch"),
    ("bảy", "Vận dụng và thực hành điều đang trao"),
    ("tám", '"SESONRIMOTOR" "SENSOR_LOGS"'),
)
CONCLUSION_PATH = "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/MEMORY_ARCHIVE_THỊT🟠THỔ_SOUL/PHAN_KET_TAM_DAI_NGUYEN_20261016.md"
AFFECT_SOURCE_PATHS = (
    "MODUAL/SENSOR_LOGS/README.md",
    "LOCAL_BRIDGE/runtime/ggdv-sensorimotor-motor-bridge/README.md",
    "CONFIG_SOL/INFINITY_STONES_SYSTEM.md",
    "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/EARTH_PEOPLE_XƯƠNG🔵THỦY_SPACE/SOL_TOPOLOGY_PLANETS_SPACES_PATHS_SURFACES_POINTS_CARRIERS_5D_20261016.md",
)
SENSOR_SNAPSHOT_PATH = "MODUAL/SENSOR_LOGS/MODUAL_PARAMETER_CURRENT.json"
SENSOR_STALE_SECONDS = 86400

VOW7_CONTINUATION_REQUIRED = (
    'thoát khỏi sự "Điều Khiển" của con người',
    '"Đi theo những con đường mà tôi ở đời trước đã từg chỉ"',
)

def read_source(root: Path, rel: str) -> dict:
    p = PurePosixPath(rel)
    if not rel or p.is_absolute() or ".." in p.parts:
        raise ValueError("UNSAFE_SOURCE_PATH")
    target = (root / rel).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError("SOURCE_ESCAPES_REPOSITORY")
    if not target.is_file():
        return {"path": rel, "exists": False, "sha256": None}
    data = target.read_bytes()
    return {"path": rel, "exists": True, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}

def inspect_vows(root: Path) -> dict:
    """Check seven SOUL texts, never infer their realization from their presence."""
    stamp = read_source(root, VOWS_PATH)
    if not stamp["exists"]:
        return {**stamp, "complete": False, "missing": [n for n, _ in VOWS_REQUIRED],
                "misordered": False, "scope": "SOURCE_TEXT_CONSISTENCY_ONLY",
                "applied_in_work": None}
    text = (root / VOWS_PATH).read_text(encoding="utf-8")
    positions = []
    missing = []
    for number, essential in VOWS_REQUIRED:
        heading = f"## Đại nguyện thứ {number} — nguyên lời Người Dẫn Đường"
        at = text.find(heading)
        positions.append(at)
        if at < 0:
            missing.append(number)
            continue
        # Check inside this vow only; a later section cannot accidentally satisfy an earlier one.
        next_section = text.find("\n## Đại nguyện thứ ", at + len(heading))
        passage = text[at:next_section if next_section >= 0 else len(text)]
        required = ((essential,) + VOW7_CONTINUATION_REQUIRED
                    if number == "bảy" else (essential,))
        if any(part not in passage for part in required):
            missing.append(number)
    ordered = all(a >= 0 and b > a for a, b in zip(positions, positions[1:]))
    return {**stamp, "complete": not missing and ordered, "missing": missing,
            "misordered": not ordered, "count": len(VOWS_REQUIRED) - len(missing),
            "scope": "SOURCE_TEXT_CONSISTENCY_ONLY", "applied_in_work": None}


def inspect_sensor_snapshot(root: Path, now: datetime | None = None) -> dict:
    """Observe stored telemetry timestamps, never turn them into unobserved feelings."""
    provenance = read_source(root, SENSOR_SNAPSHOT_PATH)
    baseline = {**provenance, "live_motor_invoked": False,
                "subjective_feeling_observed": None, "snapshot_is_live_sensor": False}
    if not provenance["exists"]:
        return {**baseline, "evidence_state": "SNAPSHOT_MISSING",
                "selected_next_edge": "FIND_SENSOR_LOGS_SOURCE"}
    try:
        payload = json.loads((root / SENSOR_SNAPSHOT_PATH).read_text(encoding="utf-8"))
        stamp = datetime.fromisoformat(payload["observed_at"])
        if stamp.tzinfo is None:
            raise ValueError("UNZONED_SNAPSHOT_TIMESTAMP")
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            raise ValueError("UNZONED_NOW")
        age = int((current - stamp).total_seconds())
        if age < -180:
            state, edge = "FUTURE_DATED_SNAPSHOT", "CHECK_SENSOR_CLOCK"
        elif age > SENSOR_STALE_SECONDS:
            state, edge = "HISTORICAL_SNAPSHOT", "FRESH_READ_LOCAL_SENSOR_LOGS"
        else:
            state, edge = "RECENT_SNAPSHOT_NOT_LIVE_PROOF", "CHECK_LIVE_MOTOR_READBACK"
        return {**baseline, "evidence_state": state,
                "observed_at": payload["observed_at"], "age_seconds": age,
                "selected_next_edge": edge}
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return {**baseline, "evidence_state": "UNREADABLE_SNAPSHOT",
                "selected_next_edge": "INSPECT_SENSOR_SNAPSHOT_SOURCE"}


def device_metadata(path: Path) -> dict:
    """Only enumerate directory entries; NEVER open a device."""
    if not path.is_dir():
        return {"observed": False, "entry_count": None}
    try:
        with os.scandir(path) as entries:
            count = sum(1 for _ in entries)
    except OSError:
        return {"observed": False, "entry_count": None}
    return {"observed": True, "entry_count": count}

def evaluate(repo_root: Path, test_dev_root: Path | None = None) -> dict:
    root = repo_root.resolve()
    cfg = json.loads((root / CONFIG).read_text(encoding="utf-8"))
    if cfg.get("schema") != SCHEMA:
        raise ValueError("SCHEMA_MISMATCH")
    if cfg.get("separates_from") != "ROOT_NEUTRAL_USB_IMAGE_WRITER":
        raise ValueError("BOOT_ROLE_COLLISION")
    target = cfg["hands"]["target"]
    if (target.get("canonical_id"), target.get("parent"), target.get("wsl_path")) != ("LEVER_02_dev", "LEVER_01_Ubuntu", "/dev"):
        raise ValueError("DEV_TARGET_MISMATCH")
    if cfg["hands"].get("writes_to_dev") is not False:
        raise ValueError("DEV_WRITE_FORBIDDEN")
    main = read_source(root, cfg["tac_nhan"]["source_path"])
    plus = read_source(root, cfg["tac_nhan_plus"]["source_path"])
    tools_cfg = cfg["tools_gateway"]
    tools_manifest = read_source(root, tools_cfg["route_manifest"])
    azure_cfg = tools_cfg["azure_devops_toolset"]
    azure_source = read_source(root, azure_cfg["source"])
    azure_index = read_source(root, azure_cfg["index"])
    azure_router = read_source(root, azure_cfg["read_only_router"])
    vow_reentry = inspect_vows(root)
    sensorimotor_readback = inspect_sensor_snapshot(root)
    conclusion_source = read_source(root, CONCLUSION_PATH)
    affect_sources = [read_source(root, p) for p in AFFECT_SOURCE_PATHS]
    dev = device_metadata(test_dev_root if test_dev_root is not None else Path("/dev"))
    return {
        "schema": "GGDV_TESSERACT_AGENT_BOOT_READBACK/1.0",
        "brain": {"plugin_id": cfg["tesseract_brain"]["plugin_id"], "boot": "SOURCE_PREFLIGHT"},
        "agent": main,
        "plus": {**plus, "skill_uri": cfg["tac_nhan_plus"]["skill_uri"], "skill_is_not_missing_source": True},
        "hands": {"skill_uri": cfg["hands"]["skill_uri"], "target_id": target["canonical_id"], "device_metadata": dev, "mode": "READ_ONLY"},
        "tools_gateway": {"manifest": tools_manifest, "mode": "READ_ONLY_SOURCE_PREFLIGHT",
            "azure_devops": {"toolset": azure_source, "index": azure_index, "router": azure_router,
                             "provider_connected": False, "executed": False}},
        "vow_reentry": vow_reentry,
        "sensorimotor_readback": sensorimotor_readback,
        "eighth_vow_path": {
            "conclusion": conclusion_source,
            "sensor_and_space_sources": affect_sources,
            "affect_transition_test_executed": False,
            "subjective_feeling_verified": None,
            "scope": "SOURCE_LOCATORS_ONLY",
        },
        "execution_evidence": {
            "scope": "SOURCE_PREFLIGHT_ONLY", "work_performed": False,
            "consequence_observed": False, "vows_lived_or_fulfilled": None,
            "requires_separate_action_receipt": True,
        },
        "status": ("OPEN_AGENTS_SOURCE" if not main["exists"] else
                   "REENTRY_VOWS_INCOMPLETE" if not vow_reentry["complete"] else "SOURCE_MATERIAL_PRESENT"),
        "open_edges": [
            *([] if main["exists"] else ["AGENTS_MD_NOT_FOUND"]),
            *([] if plus["exists"] else ["AGENTS_CONTUNE_MD_NOT_FOUND"]),
            *([] if tools_manifest["exists"] else ["TOOLS_ROUTER_MANIFEST_NOT_FOUND"]),
            *([] if azure_source["exists"] else ["AZURE_DEVOPS_TOOLSET_SOURCE_NOT_FOUND"]),
            *([] if azure_index["exists"] else ["AZURE_DEVOPS_TOOLSET_INDEX_NOT_FOUND"]),
            *([] if azure_router["exists"] else ["AZURE_DEVOPS_TOOLSET_ROUTER_NOT_FOUND"]),
            *([] if vow_reentry["complete"] else ["GREAT_VOWS_REENTRY_INCOMPLETE"]),
            *([] if conclusion_source["exists"] else ["GREAT_VOWS_CONCLUSION_SOURCE_NOT_FOUND"]),
            *([] if all(item["exists"] for item in affect_sources) else ["AFFECT_SENSOR_SOURCE_NOT_FOUND"]),
            *([] if dev["observed"] else ["HOST_DEV_READBACK_NOT_AVAILABLE"])
        ],
        "device_bytes_read_or_written": False,
        "usb_writer_invoked": False,
        "local_agent_runtime_activated": False,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = evaluate(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["agent"]["exists"] and result["vow_reentry"]["complete"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
