#!/usr/bin/env python3
"""Read-only structural validation for COMPUTER_KHI (SOL one-computer invariant)."""
import argparse
import json
from pathlib import Path

P = Path("CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER")
ROOT_COMPONENTS = ("CENTER_TAM.json", "POWER.json", "00_OPEN_0D_CONTINUITY",
                   "PUPPETEER_RUNTIME", "HOSPOSIK_AGENT_NETWORK")

def inspect(repo: Path):
    home = repo / P
    legacy = home / "SOL_COMPUTER"
    missing = [name for name in ROOT_COMPONENTS if not (home / name).exists()]
    historical = [name for name in ROOT_COMPONENTS if (legacy / name).exists()]
    state = "MIGRATION_PENDING" if legacy.exists() else (
        "CONSOLIDATED" if not missing else "INCOMPLETE")
    return {
        "schema": "SOL_SINGLE_COMPUTER_KHI_CHECK/1.0",
        "canonical": str(P),
        "one_computer_rule": True,
        "state": state,
        "legacy_path_present": legacy.exists(),
        "missing_canonical_components": missing,
        "components_still_in_legacy": historical,
        "does_not_delete_or_move_files": True,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    result = inspect(args.root.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if (not args.strict or result["state"] == "CONSOLIDATED") else 2

if __name__ == "__main__":
    raise SystemExit(main())
