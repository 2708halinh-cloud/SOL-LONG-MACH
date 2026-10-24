# Personal Tool Forge — migrated tools

This directory is a source-tracked migration workspace for personal Skills, MCP configurations, and Plugins.

## Current verified state
- Skill URI inventory: 443 installed skill entries recorded in `skills/skills-batch-001.json` (catalog only; not the full skill payloads).
- Full Skill payloads copied and read-back verified: `space-time-continuity-gate`, `alif-eprop-dual-timescale`, `agent-skills-master`.
- Other Skill payload transfers have been blocked by the source safety checker; they are not claimed as migrated.
- MCP configurations and plugin packages have not yet been migrated.

## Layout
- `skills/<skill-name>/SKILL.md`: verified Skill payloads.
- `skills/skills-batch-001.json`: installed Skill URI/description catalog.
- `mcp/`: reserved for sanitized MCP configuration manifests. Never commit tokens, OAuth refresh tokens, private keys, or credentials.
- `plugins/`: reserved for plugin manifests/source packages that can be lawfully exported and verified.
- `migration/`: receipts, source mapping, and verification notes.

## Verification rule
A migration is complete only after source content is obtained, target write succeeds, and the exact target content is read back and compared. An index entry alone is not a migrated executable artifact.
