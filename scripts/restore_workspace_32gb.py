#!/usr/bin/env python3
"""Re-enter /workspace safely; this does NOT make overlay storage persistent."""
from __future__ import annotations
import json
import os
from pathlib import Path

ROOT = Path("/workspace")
LAYOUT = [
    (ROOT, 0o755),
    (ROOT / "library-files", 0o755),
    (ROOT / "scratch", 0o755),
    (ROOT / "shared", 0o700),
    (ROOT / "shared" / "downloads", 0o700),
]

def main() -> int:
    result = {"schema": "GGDV_WORKSPACE_32GB_REENTRY/1.0", "paths": [], "persistence_verified": False}
    for path, mode in LAYOUT:
        if path.is_symlink():
            raise RuntimeError(f"Refusing symlinked workspace path: {path}")
        existed = path.exists()
        if existed and not path.is_dir():
            raise RuntimeError(f"Refusing non-directory path: {path}")
        path.mkdir(mode=mode, parents=True, exist_ok=True)
        if not existed:
            path.chmod(mode)
        result["paths"].append({
            "path": str(path),
            "existed_before": existed,
            "is_directory": path.is_dir(),
            "mode": oct(path.stat().st_mode & 0o777),
        })
    fs = os.statvfs(ROOT)
    result["fs_capacity_bytes"] = fs.f_blocks * fs.f_frsize
    result["fs_free_bytes"] = fs.f_bavail * fs.f_frsize
    result["status"] = "LAYOUT_PRESENT"
    result["note"] = "Not a cross-session storage guarantee. No files deleted or overwritten."
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
