#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
python3 "$REPO_ROOT/runtime/agent_source_gate.py" --root "$REPO_ROOT"
exec python3 "$REPO_ROOT/runtime/tesseract_agent_boot.py" --root "$REPO_ROOT"
