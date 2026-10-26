# TESSERACT Local Codex Sandbox Profile

Status: CREATED_AND_READ_BACK_ON_HOST; Codex CLI activation NOT VERIFIED because `codex` was not found on PATH during the host probe.

## Local carrier
- Root: `G:\OS_Workspace\TESSERACT_OS`
- Config: `.codex/config.toml`
- Policy: `.codex/TESSERACT_SANDBOX_POLICY.md`
- Session boot: `.codex/SESSION_BOOT.md`
- Receipt: `receipts/LOCAL_CODEX_SANDBOX_READBACK_CURRENT.json`

## Intended Codex CLI settings
- `approval_policy = "on-request"`
- `sandbox_mode = "workspace-write"`
- `network_access = false`
- writable root scoped to TESSERACT_OS only

These settings apply to a local Codex CLI session only when Codex is installed and the project is trusted. They do not modify or inject into ChatGPT's hosted/default sandbox for any account. No available supported control in this workflow exposes that hosted sandbox for direct mutation.

## Continuity contract
At session start, read the local config and task pointer; for Master Teacher work, read the actual local file, capture SHA-256 and modified time, and compare with other carriers. Before edits, create timestamped backups. After edits, perform same-carrier readback, validation, tests, and receipt.

Required sequence: ACTION -> CONSEQUENCE -> RECEIPT -> READBACK -> CONCLUSION.

## Safety
- No secrets in Git, architecture files, receipts, or logs.
- No firewall disabling as a connectivity workaround.
- User-declared device/service state is REPORTED until freshly probed.
- Stop destructive actions when source identity or target permissions are unclear; continue non-destructive tracing.
