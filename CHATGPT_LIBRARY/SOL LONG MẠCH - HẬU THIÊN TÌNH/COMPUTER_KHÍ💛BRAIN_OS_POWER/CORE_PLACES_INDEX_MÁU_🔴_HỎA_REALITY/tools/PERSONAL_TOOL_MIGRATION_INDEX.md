# SOL — Personal Tool Migration Index

**Target repository:** https://github.com/2708halinh-cloud/SOL-LONG-MACH  
**Target directory:** `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TÌNH/COMPUTER_KHÍ💛BRAIN_OS_POWER/CORE_PLACES_INDEX_MÁU_🔴_HỎA_REALITY/tools/`  
**Migration state:** `IN_PROGRESS — INDEX ONLY`  
**Created:** 2026-10-24

## Purpose
Track migration of the user's personal Skills, MCP definitions, and plugin/tool manifests into this repository while preserving source identity, licenses, secrets boundaries, and verification receipts.

## Confirmed target access
- Repository exists and authenticated GitHub connector reports push permission.
- Default branch: `main`.
- Target path has not yet been independently verified as an existing directory; Git stores directories through their files.

## Migration rules
1. Inventory each source by exact identity: source URI/repository, version or revision when available, type (`Skill`, `MCP`, `Plugin`), and access status.
2. Preserve source content where the user owns it or redistribution is permitted. For third-party material, prefer source pointers and metadata rather than copying proprietary internals.
3. Never copy credentials, API keys, OAuth tokens, private connection data, or secrets into Git.
4. Keep source identity and provenance; do not claim a tool is installed/runnable merely because its files are committed.
5. Verify every write by reading the committed file back from GitHub and recording commit SHA.
6. Mark unavailable or uninspected sources `UNKNOWN`, not migrated or clean.
7. Do not delete or disable original tools during migration.

## Initial scope
- Personal Skills: inventory installed/personal Skill sources, inspect source files where readable, migrate authorized content with provenance.
- MCP: inventory server/tool definitions and configuration schemas; exclude credentials and machine-specific secrets.
- Plugins: inventory plugin IDs, source/repository, supported runtime, and install/connection status; preserve runnable code only where authorized and compatible.
- TIME_STONE / SPACE_STONE: use as provenance, source-inventory, and relocation verification procedures, not as evidence that a transfer occurred.

## Status ledger

| Type | Discovery status | Transfer status | Verification |
|---|---|---|---|
| Personal Skills | Inventory not yet complete | Not yet transferred | Pending |
| MCP definitions | Inventory not yet complete | Not yet transferred | Pending |
| Plugins/tool manifests | Inventory not yet complete | Not yet transferred | Pending |

## Next operation
Build a source-bound inventory, then transfer in small batches. Each batch must record source identity, destination path, revision/hash where available, write receipt, and readback result.
