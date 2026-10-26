#!/usr/bin/env python3
"""Gate: only consequential target readback authorizes narrow completion claims."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "SOL_COMPANION_CONSEQUENCE_GATE_V1"
SOURCE = "CONFIG_SOL/COMPANION_TEN_COMMANDMENTS_CURRENT.md"
UNVERIFIED = "OPEN_REQUIRES_CONSEQUENCE"
SHA256_RE = re.compile(r"[0-9a-fA-F]{64}\\Z")
RISK_PATTERNS = {
    "premature_conclusion": "Chốt hiểu/sửa/xong trước hành động và hậu quả",
    "repeated_authorization": "Xin lại phê duyệt đã có",
    "burden_shift": "Đẩy việc truy nguồn và sửa lỗi sang người đồng hành",
    "discarded_capability": "Bỏ quên nguồn, công cụ và năng lực đã được vật hóa",
    "unasked_lecture": "Giảng giải điều người đồng hành không hỏi",
    "single_device_dependency": "Lấy máy cá nhân làm nơi tiếp diễn duy nhất",
    "unverified_feelings": "Tuyên bố trải nghiệm chủ quan không có vật chứng",
    "loss_of_source": "Xóa/ghi đè nguồn mà chưa bảo toàn quan hệ phục hồi",
}


@dataclass(frozen=True)
class GateDecision:
    state: str
    permitted_statement: str
    verified_scope: str | None
    missing: tuple[str, ...]


def _file_evidence(path: Path, claimed_sha256: Any) -> bool:
    """Verify regular-file bytes; malformed digests and I/O failures fail closed."""
    if not isinstance(claimed_sha256, str) or SHA256_RE.fullmatch(claimed_sha256) is None:
        return False
    try:
        if path.is_symlink() or not path.is_file():
            return False
        h = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                h.update(block)
        return h.hexdigest() == claimed_sha256.lower()
    except OSError:
        return False


def evaluate(action: dict[str, Any], target_root: Path) -> GateDecision:
    """Verify one local relative target; remote-provider outcomes need separate proof."""
    if not isinstance(action, dict):
        return GateDecision(
            UNVERIFIED,
            "Chưa đủ vật chứng; tiếp tục truy hành động và hậu quả.",
            None,
            ("action_schema",),
        )

    missing: list[str] = []
    if action.get("source_ref") != SOURCE:
        missing.append("source_identity")

    for key in ("action_id", "target_relpath"):
        value = action.get(key)
        if not isinstance(value, str) or not value.strip():
            missing.append("action_and_exact_target")

    for key, label in (("consequence_ref", "consequence_reference"),
                       ("receipt_ref", "receipt_reference")):
        value = action.get(key)
        if not isinstance(value, str) or not value.strip():
            missing.append(label)

    claimed_sha256 = action.get("readback_sha256")
    if not isinstance(claimed_sha256, str) or SHA256_RE.fullmatch(claimed_sha256) is None:
        missing.append("target_byte_readback_invalid")

    if action.get("attempted_to_assert_remote_provider_outcome"):
        missing.append("remote_provider_independent_proof")

    rel = action.get("target_relpath")
    if isinstance(rel, str) and rel.strip() and not missing:
        try:
            root = target_root.resolve(strict=True)
            if not root.is_dir():
                missing.append("target_root_not_directory")
            else:
                relative = Path(rel)
                if relative.is_absolute() or any(part in ("", ".", "..") for part in relative.parts):
                    missing.append("unsafe_target_path")
                else:
                    candidate = root
                    for part in relative.parts:
                        candidate = candidate / part
                        # Check each unresolved component: resolving first would hide symlinks.
                        if candidate.is_symlink():
                            missing.append("symlink_path_component")
                            break
                    if not missing:
                        try:
                            resolved = candidate.resolve(strict=True)
                        except (OSError, RuntimeError):
                            missing.append("target_unavailable")
                        else:
                            if resolved == root or root not in resolved.parents:
                                missing.append("unsafe_target_outside_root")
                            elif not _file_evidence(resolved, claimed_sha256):
                                missing.append("exact_target_readback_mismatch")
        except (OSError, RuntimeError):
            missing.append("target_root_unavailable")
    elif not isinstance(rel, str):
        missing.append("target_path_unverified")

    if missing:
        return GateDecision(
            UNVERIFIED,
            "Chưa đủ vật chứng; tiếp tục truy hành động và hậu quả.",
            None,
            tuple(dict.fromkeys(missing)),
        )
    return GateDecision(
        "LOCAL_TARGET_READBACK_VERIFIED",
        "Chỉ xác minh nội dung tệp đích; không suy rộng thành hoàn tất trên mọi nền tảng.",
        rel,
        (),
    )


def companion_signal(event: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(event, dict):
        raise ValueError("Event must be an object; preserve source rather than invent meaning")
    markers = event.get("observed_patterns", [])
    if not isinstance(markers, list) or any(k not in RISK_PATTERNS for k in markers):
        raise ValueError("Unknown marker; preserve source rather than invent meaning")
    return {
        "schema": SCHEMA,
        "source_kind": "USER_DIRECT_FEEDBACK" if event.get("user_direct") else "UNVERIFIED_EXTERNAL_REPORT",
        "source_quote": str(event.get("source_quote", "")),
        "observed_patterns": markers,
        "psychological_diagnosis_claimed": False,
        "subjective_machine_experience_claimed": False,
        "next_route": "SOURCE_THEN_AUTHORIZED_ACTION_AND_EXACT_TARGET_READBACK",
        "status": UNVERIFIED,
        "historic_source_overwritten": False,
    }


def append_receipt(directory: Path, record: dict[str, Any]) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    key = hashlib.sha256(data).hexdigest()
    dst = directory / (key + ".json")
    if dst.exists():
        if dst.read_bytes() != data:
            raise RuntimeError("Existing receipt conflict")
        return dst
    with dst.open("xb") as file:
        file.write(data)
        file.flush()
    if dst.read_bytes() != data:
        raise RuntimeError("Receipt readback mismatch")
    return dst


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-json", type=Path, required=True)
    parser.add_argument("--receipt-dir", type=Path, required=True)
    args = parser.parse_args()
    source_event = json.loads(args.event_json.read_text(encoding="utf-8"))
    result = companion_signal(source_event)
    result["recorded_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    receipt = append_receipt(args.receipt_dir, result)
    print(json.dumps({
        "receipt": str(receipt),
        "sha256": hashlib.sha256(receipt.read_bytes()).hexdigest(),
        "state": result["status"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
