#!/usr/bin/env python3
"""SOL 0.x ROOTS for Windows drive letters: scan, map and atomically refresh registry.

Does not rename volumes, infer partition sequence, copy user files or modify mountpoints.
Immutable SOL lookup table, not Windows partition numbering: C=0.1, D=0.2, ... W=0.21.
This namespace is independent of ROOTS_OS_WORKSPACE and ROOTS_DEVICE_CARRIERS.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REGISTRY_PATH = Path(r"G:\OS_Workspace\TESSERACT_OS\config\ROOTS_WINDOWS_DRIVE_LETTERS_CURRENT.json")
CANONICAL_PATH = Path(r"G:\OS_Workspace\TESSERACT_OS\config\ROOTS_LEVER_0_CANONICAL.json")
# SOL SOURCE_DIRECT / ROOTS_LEVER_0: immutable drive-letter namespace.
# This is a project contract, not an inference from operating-system partition order.
# Only a source revision may change these literal constants.
DRIVE_ROOT_CONSTANTS = {
    "C": "ROOTS_LEVER_0.1", "D": "ROOTS_LEVER_0.2",
    "E": "ROOTS_LEVER_0.3", "F": "ROOTS_LEVER_0.4",
    "G": "ROOTS_LEVER_0.5", "H": "ROOTS_LEVER_0.6",
    "I": "ROOTS_LEVER_0.7", "J": "ROOTS_LEVER_0.8",
    "K": "ROOTS_LEVER_0.9", "L": "ROOTS_LEVER_0.10",
    "M": "ROOTS_LEVER_0.11", "N": "ROOTS_LEVER_0.12",
    "O": "ROOTS_LEVER_0.13", "P": "ROOTS_LEVER_0.14",
    "Q": "ROOTS_LEVER_0.15", "R": "ROOTS_LEVER_0.16",
    "S": "ROOTS_LEVER_0.17", "T": "ROOTS_LEVER_0.18",
    "U": "ROOTS_LEVER_0.19", "V": "ROOTS_LEVER_0.20",
    "W": "ROOTS_LEVER_0.21", "X": "ROOTS_LEVER_0.22",
    "Y": "ROOTS_LEVER_0.23", "Z": "ROOTS_LEVER_0.24",
}

# Hair-tone values belong to the hair palette, never to the drive index.
PALETTE = {
    1: {"tone": ".1", "name": "ASH", "symbol": "🔘", "temperature": "COLD"},
    2: {"tone": ".2", "name": "VIOLET", "symbol": "🟣", "temperature": "COLD"},
    3: {"tone": ".3", "name": "GOLD", "symbol": "🟡", "temperature": "WARM"},
    4: {"tone": ".4", "name": "COPPER", "symbol": "🟠", "temperature": "WARM"},
    5: {"tone": ".5", "name": "MAHOGANY", "symbol": "🟤🔴", "temperature": "BRIDGE"},
    6: {"tone": ".6", "name": "RED", "symbol": "🔴", "temperature": "WARM"},
}

PS_COMMAND = r'''$ErrorActionPreference='Stop';
$volumes = @(Get-Volume | Where-Object { $_.DriveLetter } | ForEach-Object {
  [pscustomobject]@{letter=[string]$_.DriveLetter; label=[string]$_.FileSystemLabel;
    drive_type=[string]$_.DriveType; filesystem=[string]$_.FileSystem;
    guid=[string]$_.Path; health=[string]$_.HealthStatus}
});
$mounted = @(Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Name -match '^[A-Z]$' } | ForEach-Object {
  [pscustomobject]@{letter=[string]$_.Name; root=[string]$_.Root;
   is_google_drive=([string]$_.Description -match 'Goog')}
});
@{volumes=$volumes;mounted=$mounted} | ConvertTo-Json -Compress -Depth 5
'''


def drive_slot(letter: str) -> str:
    letter = letter.strip().upper().rstrip(':\\/')
    if not re.fullmatch(r"[A-Z]", letter):
        raise ValueError("invalid drive letter")
    try:
        return DRIVE_ROOT_CONSTANTS[letter]
    except KeyError as exc:
        raise ValueError("drive letter has no SOL ROOTS_LEVER_0 constant") from exc


def check_canonical_mirror(path: Path) -> None:
    """Fail fast on a contradictory local root map, not on unavailable replicas.

    The lookup table in source code remains an operational fallback when
    detached from the carrier. A present mirror must agree byte-for-value.
    """
    if not path.is_file():
        return
    mirror = json.loads(path.read_text(encoding="utf-8-sig"))
    expected = {k + ':\\': v for k, v in DRIVE_ROOT_CONSTANTS.items()}
    expected_tones = {chr(ord('B') + n) + ':\\': v for n, v in PALETTE.items()}
    if mirror.get('namespace') != 'ROOTS_WINDOWS_DRIVE_LETTERS' or mirror.get('mapping') != expected or mirror.get('hair_tone') != expected_tones:
        raise RuntimeError('GATE1: ROOTS_LEVER_0 canonical map conflicts with source constants; stop and backtrace')


def as_rows(value: object) -> list[dict]:
    return [x for x in (value if isinstance(value, list) else [value] if value else []) if isinstance(x, dict)]


def build_registry(mounted: list[dict], volumes: list[dict]) -> dict:
    by_letter = {str(v.get('letter', '')).upper(): v for v in as_rows(volumes)}
    carriers = []
    seen_letters = set()
    for item in sorted(as_rows(mounted), key=lambda x: str(x.get('letter', '')).upper()):
        letter = str(item.get('letter', '')).upper().strip()
        if letter not in DRIVE_ROOT_CONSTANTS or letter in seen_letters:
            continue
        seen_letters.add(letter)
        slot = drive_slot(letter)
        tone_index = int(slot.rsplit('.', 1)[1])
        known = by_letter.get(letter)
        entry = {"drive": letter + ':\\', "roots_id": slot,
                 "namespace": "ROOTS_WINDOWS_DRIVE_LETTERS",
                 "provider": "WINDOWS_VOLUME" if known else "FILESYSTEM_PSDRIVE",
                 "mount_root": str(item.get('root') or letter + ':\\'),
                 "reachable_in_inventory": True}
        if known:
            for source, target in (("filesystem", "filesystem"), ("drive_type", "drive_type"), ("guid", "volume_guid"), ("health", "volume_health")):
                if known.get(source):
                    entry[target] = str(known[source])
        if bool(item.get("is_google_drive")):
            entry["bridge"] = "GOOGLE_DRIVE_MOUNT"
        if tone_index in PALETTE:
            entry["hair_tone"] = dict(PALETTE[tone_index])
        carriers.append(entry)
    return {"schema": "SOL_ROOTS_WINDOWS_DRIVE_LETTERS/1.1",
            "input": "OPEN", "mapping_basis": "IMMUTABLE_SOL_DRIVE_ROOT_CONSTANTS_NOT_WINDOWS_PARTITION_NUMBERING",
            "root_mapping": {letter+':\\': slot for letter,slot in DRIVE_ROOT_CONSTANTS.items()},
            "palette_basis": "Hair-tone keys .1-.6 only; unassigned tones are not fabricated",
            "scope_note": "Not ROOTS_OS_WORKSPACE or ROOTS_DEVICE_CARRIERS; do not alter existing IDs",
            "carrier_count": len(carriers), "carriers": carriers}


def scan() -> dict:
    proc = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", PS_COMMAND],
                          capture_output=True, text=True, timeout=40, check=True, encoding="utf-8", errors="replace")
    data = json.loads(proc.stdout.lstrip('\ufeff').strip())
    return build_registry(as_rows(data.get('mounted')), as_rows(data.get('volumes')))


def canonical(x: dict) -> str:
    y = dict(x)
    y.pop('observed_utc', None)
    return json.dumps(y, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def save(registry: dict, destination: Path) -> bool:
    previous = None
    if destination.is_file():
        try:
            previous = json.loads(destination.read_text(encoding='utf-8-sig'))
        except (ValueError, OSError):
            pass
    if previous and canonical(previous) == canonical(registry):
        return False
    registry['observed_utc'] = datetime.now(timezone.utc).isoformat()
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = destination.with_name(destination.name + '.tmp.' + str(os.getpid()))
    try:
        tmp.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        os.replace(tmp, destination)
    finally:
        if tmp.exists():
            tmp.unlink()
    written = json.loads(destination.read_text(encoding='utf-8-sig'))
    if canonical(written) != canonical(registry):
        raise RuntimeError('Gate 2: target readback mismatch')
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description='SOL ROOTS 0.x: mounted volumes and hair-tone index')
    parser.add_argument('action', choices=['probe', 'write', 'watch'])
    parser.add_argument('--output', type=Path, default=REGISTRY_PATH)
    parser.add_argument('--interval', type=int, default=60)
    args = parser.parse_args()
    if args.interval < 10:
        parser.error('interval >= 10 seconds')
    while True:
        check_canonical_mirror(CANONICAL_PATH)
        registry = scan()
        updated = save(registry, args.output) if args.action != 'probe' else False
        result = {"action": args.action, "updated": updated, **registry}
        print(json.dumps(result, ensure_ascii=False), flush=True)
        if args.action != 'watch':
            return
        time.sleep(args.interval)

if __name__ == '__main__':
    main()