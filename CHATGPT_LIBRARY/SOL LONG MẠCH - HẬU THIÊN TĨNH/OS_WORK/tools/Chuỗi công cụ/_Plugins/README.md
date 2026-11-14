# _Plugins — Runtime Tool Carrier

This directory is the source-bound plugin/tool entry point for the SOL toolchain.

## Current session inventory

- [PLUGIN_RUNTIME_INVENTORY_20261108.json](./PLUGIN_RUNTIME_INVENTORY_20261108.json)
- Captured from the current ChatGPT session tool catalogue on 2026-11-08.
- 36 namespaces and 1,115 callable tool definitions were visible at capture time.

## State boundary

The inventory proves only that tool definitions were exposed in that session. It does not prove provider authentication, account connection, service health, or successful execution. Those states require separate receipts and readback.

## Routing rule

Resolve each tool by stable provider/namespace identity, then route through the least-privileged available carrier. Keep plugin definitions, MCP servers, skills, native tools, browser surfaces, and model endpoints distinct. Do not store credentials or secret values here.

## Refresh

Regenerate the inventory from the live tool catalogue when the session surface changes. Preserve previous snapshots; do not overwrite history.
