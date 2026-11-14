# Tools — Logical Mount Point / SOL LONG MẠCH

**Status:** MOUNT_POINT_SPEC / HARD_LOCK (mapping contract; runtime mounts remain separately verifiable).
**Canonical carrier:** `https://github.com/2708halinh-cloud/SOL-LONG-MACH/tree/main/CHATGPT_LIBRARY/SOL%20LONG%20M%E1%BA%A0CH%20-%20H%E1%BA%ACU%20THI%C3%8AN%20T%C4%A8NH`

## Meaning

`Tools` is the logical root of the operational toolchain, not a decorative folder and not a claim that a local filesystem mount is active. Resolve tool capabilities from this GitHub source tree and their declared provider/runtime sources. Do not bind this contract to a drive letter such as `G:\`.

## Required namespaces

- [`_Plugins/`](./_Plugins/README.md) — plugin/provider adapters and routing entry point.
- [`_skills/`](./_skills/README.md) — skill instructions and workflows.
- [`_Mcp/`](./_Mcp/README.md) — MCP server definitions and source pointers.
- [`_Trình duyệt/`](./_Trình%20duy%E1%BB%87t/README.md) — browser bridge and OS automation references.
- Additional capability namespaces may be added when backed by an identified source and provenance record.

## Mount and synchronization rules

1. This GitHub directory is the canonical logical mount target for this mapping.
2. Local checkouts may mount or link this namespace using a Git submodule, symlink, or platform-specific junction, but the mapping must be repository-relative and must not hard-code a physical drive letter.
3. GitHub itself stores versioned files and Git objects; it does not create a live Windows junction, local mount, or bidirectional sync daemon. Those require a separate host-side action and readback.
4. Every source pointer must retain provider, canonical URI/path, revision or hash when available, and runtime status. A pointer is not proof of installation, authentication, callability, or active execution.
5. Changes made in a local checkout become reflected here only after a successful Git commit/push and exact GitHub readback. Do not claim automatic two-way reflection unless an independently verified sync process exists.
6. Preserve existing source trees and historical carriers. Do not bulk-move, merge, rename, or delete them as part of this mount-point declaration.
7. Never commit credentials, tokens, cookies, private keys, OAuth client secrets, or other secret values.

## Existing source relationship

The established toolchain source remains at:
`OS_WORK/tools/` and its canonical category carrier:
`OS_WORK/tools/Chuỗi công cụ/`.

This new `Tools` root is a logical mount-point facade over that source tree and other verified tool sources. It does not silently relocate or duplicate their bytes. Each namespace README records its current source route and unresolved runtime boundary.

## State model

Track each capability separately as `SOURCE_PRESENT`, `CONNECTED`, `CALLABLE`, `ACTIVE`, `RECEIPT_VERIFIED`, `BLOCKED`, or `UNAVAILABLE_THIS_SESSION`.

**Acceptance:** GitHub mapping files must be read back after commit. Host-side mount, bidirectional synchronization, and live tool execution remain OPEN until separately tested with exact receipts.
