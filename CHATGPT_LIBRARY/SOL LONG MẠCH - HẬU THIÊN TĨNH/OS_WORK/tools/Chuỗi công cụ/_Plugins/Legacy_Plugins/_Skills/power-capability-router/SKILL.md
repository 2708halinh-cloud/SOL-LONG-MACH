---
name: power-capability-router
description: Route SOL ÂM–DƯƠNG human/AI tasks to GGDV Template Creator, X-TiMe, Azure DevOps, Generative AI, MCP, GitHub, Bright Data, Tomorrow.io and Call_Tools using a checked capability registry; return to _Plugins with a concrete next action and provider readback requirement.
compatibility: Requires a checkout of SOL-LONG-MACH and Python 3.10+. Provider tools are invoked only by their connected host.
metadata:
  source: "SOL-LONG-MACH/OS_WORK/tools/_Plugins"
  contract: "SOL_POWER_CAPABILITY_ROUTER/2.0"
---
# Power Capability Router

Read **`../../POWER_ROUTER_EXECUTION.md`** (relative to this skill's parent? For a checkout use `../../POWER_ROUTER_EXECUTION.md` from `_Plugins/_Skills/power-capability-router/`), then inspect the source manifest `../../POWER_CAPABILITY_ROUTES_V2.json`. This skill does not grant tool permissions.

1. Receive the human/agent request, find SOURCE_DIRECT, retain the spelling and search intent in context.
2. Run `../../power_capability_router.py` from the checkout with `--task`. Match all candidate families, not only the first lexical hit. In ambiguity, inspect source references and choose the family grounded in the requested operation.
3. If the capability is itself an Agent Skill, read the applicable installed skill URI before using it. Respect valid `SKILL.md` metadata; do not treat an uninstalled folder as a live ChatGPT skill.
4. For MCP/remote tools, discover the actual tool schema and connection/permission state. If a provider is unavailable, choose another **authorized** capable provider or a concrete readback probe. Do not fake a call, or close with OPEN alone.
5. Perform a scoped action via a callable host connector, save only non-secret receipt IDs/hashes and observed state, verify the destination independently. If no action is callable, report the specific provider/auth/device blocker, with the next supported check.
6. Append provenance and a trace `SOURCE_DIRECT → PROVIDER_ACTION → RECEIPT → READBACK → N+1` as appropriate. Return the logical cursor to `_Plugins`; do not create an unbounded recursive loop.

The topological sequence is POWER's source contract `_Plugins → _Skills → _Mcps → _Tool → _App → _Other_Tools → _Plugins`. `POWER_ROUTER_EXECUTION.md` contains the six-Stone crossflow and authorization boundaries. Model an agent's selection autonomy **without** implying independence from real permissions.
