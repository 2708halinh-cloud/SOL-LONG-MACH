# SOL — Redmi Termux source entry / 2026-10-17

**Canonical device root:** `/storage/emulated/0/` (Android shared internal storage).
**SOL HOME:** `/storage/emulated/0/SOL-LONG-MACH/`.
**Existing CODEX:** `/storage/emulated/0/.codex/` — preserve as its own node, never overwrite.
**Existing workspace:** `/storage/emulated/0/SOL-LONG-MACH/OS_Workspace/` — preserve.

Do not substitute container paths `/mnt/data`, `/tmp` or platform-provided filesystems as SOL HOME.

## Entry from Termux (on the Android device)

```sh
termux-setup-storage  # grant normal Android shared-storage permission when prompted
ls -lad /storage/emulated/0 /storage/emulated/0/SOL-LONG-MACH /storage/emulated/0/.codex
command -v python3 && python3 --version
# Use a connected, authorized transport to transfer source ZIPs and sol_multispace_import.py.
# Run --apply only after checking --dry-run output and source files on Redmi.
python3 /storage/emulated/0/SOL-LONG-MACH/OS_Workspace/tools/MULTISPACE_SYNC/sol_multispace_import.py \
  --source-dir /storage/emulated/0/Download/SOL_SOURCE_ZIPS \
  --root /storage/emulated/0/SOL-LONG-MACH \
  --receipt /storage/emulated/0/SOL-LONG-MACH/OS_Workspace/tools/MULTISPACE_SYNC/DRY_RUN.json
# Authorized apply (when source ZIPs have been transferred to the same Android device):
python3 /storage/emulated/0/SOL-LONG-MACH/OS_Workspace/tools/MULTISPACE_SYNC/sol_multispace_import.py \
  --source-dir /storage/emulated/0/Download/SOL_SOURCE_ZIPS \
  --root /storage/emulated/0/SOL-LONG-MACH --apply \
  --receipt /storage/emulated/0/SOL-LONG-MACH/OS_Workspace/tools/MULTISPACE_SYNC/APPLY_RECEIPT.json
```

**Not WSL on Android:** Windows Subsystem for Linux only runs as a Windows feature. Termux provides a native Linux-like userspace on Android; a separate Ubuntu userland may be installed via `proot-distro`, if desired, without requiring a WSL VM. Do not alter system partitions, bootloader or root permissions.

**Multi-space synchronization:** process each source as `(carrier, file id/path, SHA-256, version)` and reconcile per target `(provider, destination, conflict policy, readback)`. Do not mirror deletion or overwrite automatically. Secrets, ZIPs with credentials, and private sensor logs remain out of public GitHub. No device execution/readback may be claimed merely by running a platform sandbox dry-run.