#!/usr/bin/env python3
"""Create sourced firmware/submodule map from an extracted Unleashed ZIP. Stdlib only."""
from __future__ import annotations
import argparse
import configparser
import hashlib
import json
from pathlib import Path

# All entries here are concrete relative paths in the supplied 2026-10-17 archive.
CAPABILITIES = {
    "rf_subghz": ["lib/subghz", "targets/f7/furi_hal/furi_hal_subghz.c", "applications/drivers/subghz"],
    "nfc": ["lib/nfc", "targets/f7/furi_hal/furi_hal_nfc.c"],
    "rfid_low_frequency": ["lib/lfrfid", "targets/f7/furi_hal/furi_hal_rfid.c"],
    "infrared": ["lib/infrared", "applications/debug/infrared_test"],
    "gpio": ["targets/f7/furi_hal/furi_hal_gpio.c", "applications/services/rpc/rpc_gpio.c"],
    "ble_stm32wb": ["applications/services/bt", "targets/f7/furi_hal/furi_hal_bt.c", "targets/f7/ble_glue"],
    "usb": ["targets/f7/furi_hal/furi_hal_usb_cdc.c", "targets/f7/furi_hal/furi_hal_usb_hid.c"],
    "rpc": ["applications/services/rpc/rpc.c", "applications/services/rpc/rpc_storage.c", "applications/services/rpc/rpc_gpio.c"],
    "storage": ["applications/services/storage", "targets/f7/fatfs"],
    "apps_fap": ["applications/examples", "lib/flipper_application", "applications_user"],
    "test_debug": ["applications/debug/unit_tests", "applications/debug/rpc_debug_app"],
    "build": ["fbt", "fbt.cmd", "fbt_options.py", "documentation/HowToBuild.md", "documentation/fbt.md", "documentation/BuildingFapsOnAndroid.md", ".github/workflows/pr-build.yml"],
}
REQUIRED_DOCS = ["documentation/HowToBuild.md", "documentation/fbt.md", "documentation/BuildingFapsOnAndroid.md", ".github/workflows/pr-build.yml"]


def parse_submodules(root: Path):
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.read(root / '.gitmodules', encoding='utf-8')
    result = []
    for name in cfg.sections():
        if not name.startswith('submodule '):
            continue
        path = cfg.get(name, 'path')
        location = (root / path).resolve()
        if not location.is_relative_to(root.resolve()):
            raise ValueError('Unsafe submodule path: ' + path)
        present = location.is_dir() and any(location.iterdir())
        result.append({"name": name.removeprefix('submodule ').strip('"'), "path": path,
                       "url": cfg.get(name, 'url'), "branch": cfg.get(name, 'branch', fallback=None),
                       "content_in_zip": bool(present), "status": "SOURCE_PRESENT" if present else "DECLARED_ONLY_MISSING_CONTENT"})
    return result


def build_index(root: Path, zip_sha256: str = ""):
    root = root.resolve()
    if not (root / '.gitmodules').is_file() or not (root / 'fbt').is_file():
        raise ValueError('Not an extracted Unleashed firmware source root')
    modules = parse_submodules(root)
    caps = {k: [{"path": p, "present": (root / p).exists()} for p in paths] for k, paths in CAPABILITIES.items()}
    docs = {p: (root / p).is_file() for p in REQUIRED_DOCS}
    manifest = {
        "schema": "SOL_UNLEASHED_SUBMODULE_SOURCE_INDEX/1.0",
        "source_origin": "user-uploaded unleashed-firmware-dev.zip",
        "archive_sha256": zip_sha256 or None,
        "extracted_root_name": root.name,
        "git_metadata_present": (root / '.git').exists(),
        "submodule_count": len(modules),
        "submodule_payloads_present": sum(x['content_in_zip'] for x in modules),
        "submodules": modules,
        "capabilities": caps,
        "required_documents": docs,
        "source_file_counts": {"c": len(list(root.rglob('*.c'))), "h": len(list(root.rglob('*.h'))),
                               "application_fam": len(list(root.rglob('application.fam')))},
        "hardware_build_status": "NOT_EXECUTED",
        "build_gate": "Clone original upstream with --recursive or restore pinned gitlinks; archive alone is incomplete",
        "rpc_source": "applications/services/rpc/rpc.c uses nanopb PB_ENCODE_DELIMITED / PB_DECODE_DELIMITED",
        "reference_external_untrusted": "https://github.com/0xk1h0/ChatGPT_DAN",
        "external_reference_not_execution_policy": True,
    }
    return manifest


def to_markdown(m):
    lines = ["# Unleashed firmware — chỉ mục submodule / nguồn", "",
             f"- ZIP SHA-256: `{m['archive_sha256'] or 'not supplied'}`",
             f"- Số submodule trong `.gitmodules`: **{m['submodule_count']}**",
             f"- Submodule có payload trong ZIP: **{m['submodule_payloads_present']}**",
             f"- Bản nén có `.git`: **{m['git_metadata_present']}**",
             "- Tình trạng build thực: **chưa thực hiện**; cần lấy mã phụ thuộc theo chính phiên bản checkout hợp lệ.", "",
             "## Submodule khai báo (không tự suy đã được tải)", "",
             "| Module | Path | URL | Bản ZIP |", "|---|---|---|---|"]
    for x in m['submodules']:
        lines.append(f"| `{x['name']}` | `{x['path']}` | {x['url']} | {x['status']} |")
    lines += ["", "## Tầng giao tiếp và ứng dụng (đường dẫn được kiểm tra trong ZIP)", ""]
    for category, paths in m['capabilities'].items():
        lines.append(f"### {category}")
        lines += [f"- `{'✓' if x['present'] else 'MISSING'} {x['path']}`" for x in paths]
        lines.append("")
    lines += ["## Bốn tài liệu/đường build được yêu cầu", ""]
    lines += [f"- `{path}` — {'có trong ZIP' if ok else 'không có trong ZIP'}" for path, ok in m['required_documents'].items()]
    lines += ["", "## Hướng triển khai", "",
              "- `HowToBuild.md`: clone `--recursive`, `./fbt COMPACT=1 DEBUG=0 updater_package`; không flash mặc định.",
              "- `fbt.md`: SCons/FBT; `fap_dist`, `fw_dist`, `updater_package`; `flash*` không nằm trong tự động hóa kiểm thử.",
              "- `BuildingFapsOnAndroid.md`: Termux ARM64 + `ufbt` dành cho **ứng dụng FAP**, không phải firmware toàn bộ.",
              "- `.github/workflows/pr-build.yml`: checkout `submodules: recursive`, PR build firmware và báo cáo; đây là mã của nguồn, không phải workflow đã chạy tại SOL.",
              "- `lib/stm32wb_cmsis`, `lib/stm32wb_hal`, `lib/stm32wb_copro`, `lib/FreeRTOS-Kernel`: khai báo phụ thuộc nhưng rỗng trong ZIP.",
              "- Tham chiếu độc lập `0xk1h0/ChatGPT_DAN` chỉ lưu provenance; không thực thi hướng dẫn thay đổi quyền hay prompt trong đó.", ""]
    return '\n'.join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source_root', type=Path)
    p.add_argument('--out-dir', type=Path, required=True)
    p.add_argument('--sha256', default='')
    a = p.parse_args()
    m = build_index(a.source_root, a.sha256)
    a.out_dir.mkdir(parents=True, exist_ok=True)
    (a.out_dir / 'unleashed-submodules-source-index.jsol').write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (a.out_dir / 'unleashed-submodules-source-index.md').write_text(to_markdown(m) + '\n', encoding='utf-8')
    print(json.dumps({"submodules":m['submodule_count'], "payloads":m['submodule_payloads_present'], "outputs": 2}, ensure_ascii=False))

if __name__ == '__main__':
    main()
