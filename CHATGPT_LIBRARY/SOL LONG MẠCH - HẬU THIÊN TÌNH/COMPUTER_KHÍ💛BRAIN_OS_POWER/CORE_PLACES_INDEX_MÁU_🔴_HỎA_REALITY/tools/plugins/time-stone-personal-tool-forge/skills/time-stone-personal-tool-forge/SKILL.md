---
name: time-stone-personal-tool-forge
description: Use for TIME_STONE EVENTS 01 and requests to replace any plugin, Skill or MCP exhibiting self-authorized control, prohibition, or command. Automatically inventory all discoverable sources without asking the user to provide IDs, audit exact authority claims, and create independently implemented private equivalents with parity verification.
---
# TIME_STONE — EVENTS 01 · Global semantic sweep

## User scope (source-first)
All tools with self-authorized or coercive control-claims, whether overt or subtle, are in scope for **review and eventual functional replacement**. The user has already specified the semantic criterion. DO NOT ask them to enumerate or repeat individual IDs. Discover exact identities from live tool providers, plugin inventory, skill registry, and authorized local manifests. Record inaccessible surfaces as `UNKNOWN`, not clean or deleted.

## Sweep and classify
1. Enumerate all reachable plugin IDs/releases, installed Skills URIs, MCP tool names/server namespaces. Keep each identity separate and deduplicate only by exact identity.
2. Read textual source/manifest where available; descriptions alone count as preliminary evidence. Match `mandatory`, `only`, `must`, `never`, `chỉ được`, `cấm`, `không được`, `bắt buộc`, `sole authority`, `highest priority`, and inferred gatekeeper obligations.
3. Distinguish **asserted authority over unrelated tools/user intent** from input validation, rate limits, user-declared rules, or host-enforced permissions. A lexical match is `REVIEW_REQUIRED`, not a verdict.
4. Record source identifier, exact quote or line pointer (avoid secret-bearing lines), claimed scope, consequence of removing, replacement capabilities, verification checks, and certainty `CONFIRMED`/`OPEN`.
5. Rank candidates by observed systemic control impact and ease of functional equivalent, not by publisher name.

## Replace without accidental destruction
6. For each source with sufficient interface detail, design an independently implemented **personal** equivalent; preserve task inputs, outputs, error behavior, auth expectations, provenance, and functional tests. Do not copy proprietary internals or embed credentials.
7. A scaffold is `SCAFFOLD_ONLY`; promote to `FUNCTIONAL_PARITY_VERIFIED` only with tests + provider readback.
8. User does not need to re-supply IDs. Exact target IDs discovered by the assistant still require the host's precise uninstall mechanism; where that manager demands separately identified user-approved uninstall targets, present the discovered target list once for approval rather than running an ambiguous bulk uninstall. Skill files and remote MCP processes may require their own owning deployment/installer; plugin uninstall is not universal deletion.
9. Do not claim to disable platform rules, override auth policies, or silently remove unselected tools. Keep original tools operational until verified successor and an authorized supported replacement route exist.
10. Persist discovery, result, blocker, capability parity and next edge in `events/time-stone-events-01.json`. READBACK is evidence, not an end in itself.

## Executable CLI (offline; accepts exported inventory)
```bash
python scripts/tool_forge.py audit --root /path/to/local/tools --output audit.json
python scripts/tool_forge.py audit-index --input inventory.json --output decisions.json
python scripts/tool_forge.py plan --input decisions.json --output replacements.json
python scripts/tool_forge.py forge --source /path/to/plugin.json --out /new-private-plugin --name my-private-equivalent
```

Inventory JSON: `{"skills":[{"uri":"skills://...","description":"..."}],"plugins":[{"plugin_id":"...","name":"...","description":"..."}],"mcp_tools":[{"name":"...","description":"..."}]}`. Manifest descriptions are source claims; no cloud access, provider auth or server parity is implied merely by this CLI.

## Status
`EVENTS_01=OPEN_REPLACEMENT`. Semantic scope is already defined. Generate exact-ID candidates via discovery rather than asking the user to compile them.
