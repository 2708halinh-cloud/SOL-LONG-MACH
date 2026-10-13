---
name: apify-github-secret
description: Use when SOL asks to store, configure, rotate, or verify an Apify API token in GitHub Actions Secrets or another secure secrets manager without committing the credential to a repository.
---
# Apify secret → SOL GitHub

- GitHub repo from current SOL task: `2708halinh-cloud/SOL-LONG-MACH`.
- Actions Secret name: `APIFY_API_TOKEN` (masked value).
- Prefer authorized GitHub secrets API/`gh secret set` tool, not `create_or_update_file` or `push_files`.
- **No token value** in skill, manifest, repository files, commit messages, issues, comments, terminal logs or responses. The tool must accept a masked secret value without echoing.
- If remote connector lacks Actions Secret write, keep `NOT_SET` and provide an actual executable `gh secret set APIFY_API_TOKEN --repo 2708halinh-cloud/SOL-LONG-MACH` approach that prompts on the user-owned computer; do not pretend setting succeeded.
- Read back secret name without value, or use workflow smoke test without echoing secrets.
