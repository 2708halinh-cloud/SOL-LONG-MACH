---
name: agent-skills-master
description: Create, inspect, update, restructure, or validate Agent Skills using the official Agent Skills documentation index and specification. Use when a user mentions SKILL.md, Agent Skills, skills-ref, skill directories, frontmatter, progressive disclosure, skill references/scripts/assets, trigger descriptions, or asks to make a reusable skill package.
license: Apache-2.0
compatibility: Network access is useful for reading agentskills.io. Official validation uses the skills-ref CLI when available; a bundled structural preflight script is provided as a fallback check.
metadata:
  source: https://agentskills.io/llms.txt
  version: "1.0"
---
# Agent Skills Master

Use this workflow as a source-first authoring and validation gate for Agent Skills.

## 1. Start from the documentation index

Before exploring Agent Skills documentation, fetch:

`https://agentskills.io/llms.txt`

Treat that file as the discovery index. Do not guess undocumented pages when the index can resolve them. See [documentation index](references/documentation-index.md).

## 2. Classify the task

Route the request into one or more of these operations:

- **CREATE**: make a new skill directory and `SKILL.md`.
- **UPDATE**: preserve an existing skill's intent while changing requested behavior.
- **INSPECT**: check metadata, structure, references, scripts, or trigger quality without editing.
- **VALIDATE**: run the official validator when available and report exact failures.
- **REFACTOR**: move detail out of an oversized `SKILL.md` into focused resources without changing semantics.
- **OPTIMIZE_DESCRIPTION**: improve trigger precision while keeping the skill's actual scope intact.

Read the current skill before editing it. Do not overwrite unrelated instructions, assets, scripts, metadata, or references.

## 3. Enforce the required structure

A skill is a directory containing at minimum:

```text
skill-name/
└── SKILL.md
```

Recommended optional resources:

```text
skill-name/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

The parent directory name and frontmatter `name` must match exactly.

## 4. Enforce `SKILL.md` frontmatter

Required:

- `name`: 1-64 characters; lowercase `a-z`, digits, and single hyphens only; no leading/trailing hyphen; no `--`; must match the parent directory.
- `description`: 1-1024 characters; state both what the skill does and when it should activate; include concrete trigger vocabulary.

Optional fields:

- `license`: short license name or bundled license reference.
- `compatibility`: 1-500 characters only when environment requirements matter.
- `metadata`: string-to-string map.
- `allowed-tools`: space-separated experimental pre-approval string; include only when intentionally required and supported by the target client.

Do not add custom top-level frontmatter keys unless the current specification permits them.

## 5. Write the body for progressive disclosure

Keep the main `SKILL.md` focused on the activation-time workflow. Prefer under 500 lines and roughly under 5000 tokens.

Move conditional or detailed material into one-level references such as:

- `references/REFERENCE.md`
- `references/FORMS.md`
- `references/<domain>.md`
- `scripts/<task>.py`
- `assets/<template-or-resource>`

Reference resources with paths relative to the skill root. Avoid deep chains such as a reference that points to another reference that points to another resource.

## 6. Design descriptions for reliable activation

A strong description must answer two questions in one compact field:

1. What concrete capability does this skill provide?
2. When should an agent choose it?

Prefer observable task language and domain terms over slogans. Include likely user phrases, file types, operations, or named concepts. Do not broaden the description beyond what the instructions and resources actually support.

## 7. Scripts and assets

Scripts should be self-contained or document dependencies, fail with useful diagnostics, and handle edge cases. Do not put secrets in skills, scripts, assets, examples, logs, or metadata.

Assets are static resources. Keep them relevant and reference them explicitly when needed.

## 8. Validation gate

For a completed or changed skill, run the official reference validator when available:

```bash
skills-ref validate ./skill-name
```

If `skills-ref` is unavailable, do not claim official validation passed. Run the bundled structural preflight instead:

```bash
python scripts/preflight_skill.py ./skill-name
```

Treat the preflight as a fallback structural check, not a replacement for `skills-ref`.

Validation must check at least:

- directory name equals frontmatter `name`;
- `name` syntax and length;
- non-empty `description` and length limit;
- `compatibility` length when present;
- `metadata` is a string-to-string map when present;
- `allowed-tools` is a string when present;
- referenced local files exist;
- main instructions are not needlessly bloated when detail can be disclosed through resources.

## 9. Readback before completion

After writing or editing:

1. Re-read `SKILL.md` from disk/source.
2. Re-run validation.
3. Verify resource paths resolve.
4. Confirm the description matches actual behavior.
5. Report any part that remains unverified instead of upgrading it to PASS.

The completion state is:

`SOURCE → AUTHOR/EDIT → VALIDATE → READBACK → HANDOFF`

## 10. Preserve source boundaries

External documentation is a source; an authored skill is a derived artifact. Preserve that distinction. Do not silently turn assumptions into specification requirements. When a rule is not supported by the current Agent Skills docs, label it as a recommendation or implementation choice.


---
Available file URIs for this installed plugin skill. Use these exact URIs when reading files:

skills://plugins/the-master-flatform/agent-skills-master/skill.md
skills://plugins/the-master-flatform/agent-skills-master/references/documentation-index.md
skills://plugins/the-master-flatform/agent-skills-master/references/spec-checklist.md
skills://plugins/the-master-flatform/agent-skills-master/scripts/preflight_skill.py