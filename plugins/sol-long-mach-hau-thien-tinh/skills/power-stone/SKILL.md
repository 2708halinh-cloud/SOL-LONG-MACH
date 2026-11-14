---
name: power-stone
description: Use when the user invokes POWER STONE or legacy @ALL, asks SOL to sense the whole relevant capability field, recover a missing tool/skill/plugin, or continue through capability selection without blindly calling everything.
---

# POWER STONE — SOL Capability Router

POWER STONE is the current project-facing name for legacy `@ALL` within SOL Capability Forge.

## Function
1. Re-enter prioritized Project sources relevant to the task.
2. Inventory only capabilities that could materially affect the current goal.
3. Separate `SOURCE_PRESENT`, `CONNECTED`, `CALLABLE`, `ACTIVE`, `RECEIPT_VERIFIED`, `BLOCKED`, and `UNAVAILABLE_THIS_SESSION`.
4. Choose the smallest sufficient authorized route.
5. Execute real actions when supported.
6. When a capability is missing but reusable, route to SOL Capability Forge for update/create rather than inventing a fake capability.
7. Preserve source identity, history, and causal distinctions.

## Legacy alias
If an older source says `@ALL`, interpret it as an alias pointing here unless that source explicitly defines a different historical meaning. Do not rewrite historical carriers solely to rename the token.

## Power boundary
POWER STONE is a routing/capability metaphor in this project. It does not grant hidden permissions, background execution, secret access, physical-device control, or truth authority.

## Completion state
A POWER STONE pass is complete only for the scope actually observed and acted on. Unavailable providers remain unavailable; local/runtime edges remain unverified until receipts exist.
