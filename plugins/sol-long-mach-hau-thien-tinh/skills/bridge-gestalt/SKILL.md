---
name: bridge-gestalt
description: Use when a local path, worktree, localhost bridge, device route, runner, mount, or connector disappears or moves and SOL must recover the intended topology without fixating on stale literal addresses. Complements linear troubleshooting with whole-field spatial reconstruction and grounded materialization.
---

# SOL RIGHT HEMISPHERE — BRIDGE GESTALT

## Goal
Preserve the user's intended connection while allowing the physical/logical carrier to change.

`BROKEN_LITERAL_PATH != BROKEN_OBJECTIVE`

## Whole-field reconstruction
When a route fails, identify the full shape before editing one string:
- intended endpoint/service/device;
- current control plane;
- durable repository/source identity;
- possible local roots/mounts/worktrees;
- available transport carriers;
- readback location.

Represent internally as:
`OBJECTIVE ↔ IDENTITY ↔ CARRIER_SET ↔ EXECUTOR ↔ ENDPOINT ↔ READBACK`.

## Semantic anchors over literal addresses
Prefer stable anchors such as repository origin, plugin ID, task name, service name, endpoint role, device identity, or source ID over generated paths.

Examples:
- locate a repository by `git remote origin`, not a generated worktree name;
- locate a service by role/port plus executable identity, not one stale filesystem path;
- use a stable scheduled task to re-enter a changing worktree graph.

## Divergent recovery
Generate at least two feasible recovery carriers when one path is broken, for example:
- existing local watcher;
- self-hosted runner;
- stable clone + scheduled task;
- connected remote desktop/local MCP;
- provider-native action.

Choose the smallest path that can produce a real consequence now. Keep alternates as fallback, not as simultaneous duplicate execution.

## Materialization
If a safe authorized carrier is callable, mutate the system rather than only explaining the failure:
`OBSERVE → RECONSTRUCT_TOPOLOGY → SELECT_CARRIER → MATERIALIZE → PROBE → RECEIPT → READBACK`.

Do not claim connection from config existence alone.

## STOP gate
A failure message is not a completion condition. If another grounded carrier remains callable, reroute in the same response.

`FIRST_PATH_FAILED → ALTERNATE_CARRIER → ACTION`, not `FIRST_PATH_FAILED → REPORT → STOP`.

## Boundaries
- Do not invent live device state.
- Do not treat localhost from cloud as the user's localhost.
- Do not expose secret bytes in receipts.
- Do not erase history when replacing a stale path.
- Prefer root-neutral discovery and stable identities.

## Handoff
Once the route exists and readback passes, hand concise wording/presentation to `consistent-editor` when polished communication is needed.
