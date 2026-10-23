from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

try:
    from .sensor_root_resolver import resolve_sensor_root
except ImportError:  # direct script invocation
    from sensor_root_resolver import resolve_sensor_root

# Live source has to be observed before any snapshot writes happen.
SENSOR_ROOT = resolve_sensor_root()
REPO_ROOT = Path(r"D:\SOL_LONG_MACH\MODEL\repo")
DEST_ROOT = REPO_ROOT / "MODUAL" / "SENSOR_LOGS"
SOURCE_DIR = DEST_ROOT / "source"
LIVE_DIR = DEST_ROOT / "live"

BULK_NAME = "_SESORIMOTOR__WINDOWS__XIAOMI12__REDMINOTE14PRO__0000THEMASTERTEACHER__R000_075203003486__.CSV"
LIVE_NAME = "_SESORIMOTOR__{WINDOWS)__XIAOMI12__REDMINOTE14PRO__0000THEMASTERTEACHER__R000_075203003486__.CSV"
CONTROL_FILES = ["telemetry_buffer_sync.py", "START_TELEMETRY_SYNC.bat", "modual_github_sync.py"]
BRANCH = "sol-long-mach-current"


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def _sha256(path: Path, chunk: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _first_line(path: Path) -> str:
    if not path.exists():
        return ""
    with path.open("r", encoding="utf-8-sig", errors="replace") as f:
        return f.readline().rstrip("\r\n")


def _snapshot_one(path: Path, role: str) -> dict:
    if not path.exists():
        return {"name": path.name, "role": role, "exists": False}
    st = path.stat()
    return {
        "name": path.name,
        "role": role,
        "exists": True,
        "source_path": str(path),
        "bytes": st.st_size,
        "modified_at": datetime.fromtimestamp(st.st_mtime, timezone.utc).astimezone().isoformat(),
        "sha256": _sha256(path),
    }


def _run_git(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        errors="replace",
    )


def build_repo_snapshot() -> dict:
    DEST_ROOT.mkdir(parents=True, exist_ok=True)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    LIVE_DIR.mkdir(parents=True, exist_ok=True)

    bulk = SENSOR_ROOT / BULK_NAME
    live = SENSOR_ROOT / LIVE_NAME

    for name in CONTROL_FILES:
        src = SENSOR_ROOT / name
        if src.exists():
            shutil.copy2(src, SOURCE_DIR / name)

    # Never copy raw sensor rows into the repository. Keep the compatibility
    # carrier header-only; the original live source remains on its source root.
    bulk_info = _snapshot_one(bulk, "MODUAL_BULK_LOCAL_SOURCE")
    live_info = _snapshot_one(live, "MODUAL_LIVE_PARAMETER_CARRIER")

    bulk_header = _first_line(bulk)
    live_header = _first_line(live)
    bulk_header_text = bulk_header + "\n" if bulk_header else ""
    live_header_text = live_header + "\n" if live_header else ""

    (DEST_ROOT / "BULK_HEADER_CURRENT.csv").write_text(bulk_header_text, encoding="utf-8")
    (DEST_ROOT / "BULK_LATEST_CURRENT.csv").write_text(bulk_header_text, encoding="utf-8")
    (DEST_ROOT / "LIVE_HEADER_CURRENT.csv").write_text(live_header_text, encoding="utf-8")
    (DEST_ROOT / "LIVE_LATEST_CURRENT.csv").write_text(live_header_text, encoding="utf-8")
    (LIVE_DIR / LIVE_NAME).write_text(live_header_text, encoding="utf-8")

    state = {
        "schema": "GGDV_MODUAL_SENSOR_LOGS_GITHUB_STATE/1.0",
        "observed_at": _now(),
        "source_root": str(SENSOR_ROOT),
        "source_semantics": "LOCAL_MODUAL_BYTES_AND_INTERMEDIATE_DEVICE_TELEMETRY",
        "github_role": "LAW_AND_CURRENT_STATE_NOT_BULK_ARCHIVE",
        "bulk": bulk_info,
        "live": live_info,
        "sync_policy": {
            "bulk_raw_committed": False,
            "bulk_representation": ["sha256", "bytes", "modified_at", "header"],
            "live_raw_committed": False,
            "live_representation": ["sha256", "bytes", "modified_at", "header"],
            "latest_row_committed": False,
            "control_files_committed": True,
        },
        "privacy_policy": {
            "current_snapshot_files": "HEADER_ONLY",
            "raw_sensor_rows_committed": False,
            "historical_git_versions_rewritten": False,
        },
    }
    state_path = DEST_ROOT / "MODUAL_PARAMETER_CURRENT.json"
    if state_path.exists():
        try:
            previous_state = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError("CURRENT_STATE_UNREADABLE_REFUSE_OVERWRITE") from exc
        if not isinstance(previous_state, dict):
            raise RuntimeError("CURRENT_STATE_NOT_OBJECT_REFUSE_OVERWRITE")
        # Keep additive provenance/history fields from the existing state file.
        for key, value in previous_state.items():
            if key not in state:
                state[key] = value
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    readme = (
        "# MODUAL / SENSOR_LOGS — GitHub Current State\n\n"
        f"OBSERVED_SENSOR_SOURCE: {SENSOR_ROOT}\n\n"
        f"- {BULK_NAME}: bulk telemetry local carrier. Raw bytes remain on local/bulk storage; GitHub keeps digest + header + latest row.\n"
        f"- {LIVE_NAME}: live/intermediate MODUAL parameter carrier; copied into live/.\n"
        "- source/: executable control files that generate/sync MODUAL state.\n"
        "- MODUAL_PARAMETER_CURRENT.json: current compact state/readback.\n\n"
        "AUTO_SYNC:\n"
        f"Sensor scripts run against verified source {SENSOR_ROOT}; no empty D: recreation.\n\n"
        "GitHub is used here as Law/State, not as the bulk telemetry store.\n"
    )
    (DEST_ROOT / "README.md").write_text(readme, encoding="utf-8")
    return state


def git_sync() -> dict:
    if not REPO_ROOT.exists():
        return {"success": False, "error": "REPO_ROOT_MISSING", "repo": str(REPO_ROOT)}

    branch = _run_git(["branch", "--show-current"])
    if branch.returncode != 0 or branch.stdout.strip() != BRANCH:
        return {
            "success": False,
            "error": "UNEXPECTED_BRANCH",
            "branch": branch.stdout.strip(),
            "expected": BRANCH,
        }

    _run_git(["add", "-A", "--", "MODUAL/SENSOR_LOGS"])
    diff = _run_git(["diff", "--cached", "--quiet", "--", "MODUAL/SENSOR_LOGS"])
    if diff.returncode == 0:
        return {"success": True, "changed": False, "branch": BRANCH}

    msg = "MODUAL: auto-sync SENSOR_LOGS current state"
    commit = _run_git(["commit", "--only", "-m", msg, "--", "MODUAL/SENSOR_LOGS"], timeout=120)
    if commit.returncode != 0:
        return {
            "success": False,
            "error": "GIT_COMMIT_FAILED",
            "stdout": commit.stdout[-4000:],
            "stderr": commit.stderr[-4000:],
        }

    push = _run_git(["push", "origin", f"HEAD:{BRANCH}"], timeout=180)
    if push.returncode != 0:
        return {
            "success": False,
            "error": "GIT_PUSH_FAILED",
            "commit": _run_git(["rev-parse", "HEAD"]).stdout.strip(),
            "stdout": push.stdout[-4000:],
            "stderr": push.stderr[-4000:],
        }

    return {
        "success": True,
        "changed": True,
        "branch": BRANCH,
        "commit": _run_git(["rev-parse", "HEAD"]).stdout.strip(),
        "push_stdout": push.stdout.strip(),
        "push_stderr": push.stderr.strip(),
    }


def sync() -> dict:
    state = build_repo_snapshot()
    git_result = git_sync()
    result = {"state": state, "git": git_result}
    status_path = SENSOR_ROOT / "MODUAL_GITHUB_SYNC_CURRENT.json"
    status_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(sync(), ensure_ascii=False, indent=2))
