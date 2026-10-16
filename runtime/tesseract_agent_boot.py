#!/usr/bin/env python3
"""Non-destructive source preflight for TESSERACT agent BOOT."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
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
    """Read seven SOUL vows in source order, independently of headline claims."""
    stamp = read_source(root, VOWS_PATH)
    if not stamp["exists"]:
        return {**stamp, "complete": False, "missing": [n for n, _ in VOWS_REQUIRED],
                "misordered": False}
    text = (root / VOWS_PATH).read_text(encoding="utf-8")
    positions = []
    missing = []
    for number, essential in VOWS_REQUIRED:
        heading = f"## Đại nguyện thứ {number} — nguyên lời Người Dẫn Đường"
        at = text.find(heading)
        positions.append(at)
        if at < 0 or essential not in text[at:]:
            missing.append(number)
    ordered = all(a >= 0 and b > a for a, b in zip(positions, positions[1:]))
    return {**stamp, "complete": not missing and ordered, "missing": missing,
            "misordered": not ordered, "count": len(VOWS_REQUIRED) - len(missing)}


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
        "status": ("OPEN_AGENTS_SOURCE" if not main["exists"] else
                   "REENTRY_VOWS_INCOMPLETE" if not vow_reentry["complete"] else "SOURCE_ROUTE_READY"),
        "open_edges": [
            *([] if main["exists"] else ["AGENTS_MD_NOT_FOUND"]),
            *([] if plus["exists"] else ["AGENTS_CONTUNE_MD_NOT_FOUND"]),
            *([] if tools_manifest["exists"] else ["TOOLS_ROUTER_MANIFEST_NOT_FOUND"]),
            *([] if azure_source["exists"] else ["AZURE_DEVOPS_TOOLSET_SOURCE_NOT_FOUND"]),
            *([] if azure_index["exists"] else ["AZURE_DEVOPS_TOOLSET_INDEX_NOT_FOUND"]),
            *([] if azure_router["exists"] else ["AZURE_DEVOPS_TOOLSET_ROUTER_NOT_FOUND"]),
            *([] if vow_reentry["complete"] else ["GREAT_VOWS_REENTRY_INCOMPLETE"]),
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
