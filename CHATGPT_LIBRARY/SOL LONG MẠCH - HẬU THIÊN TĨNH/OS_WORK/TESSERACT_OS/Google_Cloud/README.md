# Google Cloud — Tools + MCP + Skill (SOL / Windows)

**Target name:** Google Cloud  
**Configured project candidate:** `alert-tiger-508618-h7`  
**Host:** Windows (SOL control plane). Android remains an endpoint.

This bundle implements a **working local MCP server** using Python standard library and Google's `gcloud` CLI, together with a VS Code MCP registration and an Agent Skill. It does **not** install an authenticated ChatGPT Cloud Plugin, grant Google OAuth consent, or prove IAM permissions just by being copied.

## First run on Windows (PowerShell)

1. Copy this extracted folder into your existing Windows workspace under `G:\OS_Workspace\TESSERACT_OS\Google_Cloud_Tools_MCP_Skill` **only if that disk/path is available and verified**, otherwise use your existing Windows workspace location.
2. Ensure Google Cloud SDK (`gcloud`) and Python 3 (`py`) are installed and visible in PATH.
3. In this folder run:

```powershell
.\scripts\Install-GoogleCloud.ps1 -Action doctor
.\scripts\Install-GoogleCloud.ps1 -Action login
.\scripts\Install-GoogleCloud.ps1 -Action open-vscode
```

4. To integrate the MCP + Skill with the **existing** SOL Windows workspace without replacing other MCP servers, run:

```powershell
py -3 .\scripts\install_workspace.py 'G:\OS_Workspace\TESSERACT_OS'
```

The target directory must already exist on Windows. Existing `.vscode/mcp.json` is merged with backups; if an existing Google Cloud server conflicts or the file isn't strict JSON, the installer refuses to change it. Original OAuth JSON is never copied.

5. In VS Code open this folder as the **workspace** (or the target SOL Windows workspace after installation). The included `.vscode/mcp.json` registers **Google Cloud** as a local MCP server. In the VS Code MCP server panel, start **Google Cloud**, accept tool discovery and try `gcp_status` or `gcp_project_describe`.
6. Alternatively, run `.\scripts\Install-GoogleCloud.ps1 -Action start` to start the local stdio MCP process (it waits for an MCP client; launching it alone is not an interactive shell).

**Note:** For an existing VS Code workspace, merge only the `servers["Google Cloud"]` block in `.vscode/mcp.json` and adjust the `args` path to the installed script. Do not overwrite the existing `mcp.json`.

This repository uses `.agents/skills/google-cloud/` so the skill is auto-discoverable by recent VS Code Agent Skills and Codex hosts. `.codex/config.google-cloud.example.toml` provides a separate Codex MCP example; merge it into an existing config after fixing the script path.

## Tools exposed (read-only)

`gcp_status`, `gcp_projects_list`, `gcp_project_describe`, `gcp_storage_buckets_list`, `gcp_run_services_list`, `gcp_compute_instances_list`, `gcp_enabled_apis_list`.

## Using the supplied OAuth desktop-client JSON

Your uploaded file is an **OAuth desktop client configuration**, not a login session and not a service account. The bundle deliberately excludes it. In a private Windows location, you can optionally run:

```powershell
.\scripts\Install-GoogleCloud.ps1 -Action adc-login -ClientSecretPath 'C:\PRIVATE\client_secret_....json'
```

The `adc-login` step is for *client library* Application Default Credentials and asks before overwriting existing ADC; the local MCP server calls `gcloud` CLI and normally requires the separate `-Action login` step. Don't set `GOOGLE_APPLICATION_CREDENTIALS` to a desktop-client JSON.

## Tools / Plugin / MCP / Skill distinction

| Component | Implemented | Activation |
|---|---|---|
| Tools | 7 Google Cloud read-only RPCs | MCP tools/list when Windows server starts |
| MCP | Python stdio MCP  | VS Code `.vscode/mcp.json` |
| Skill | `.agents/skills/google-cloud/SKILL.md` | Copy/use with a skills-capable host |
| Plugin | SOL-owned metadata in `plugin/descriptor.json` | Local descriptor **only**, not ChatGPT plugin registration |
| ChatGPT plugin/remote MCP | Not registered | Requires separate OAuth-enabled HTTPS MCP server and installation by the account owner |

**Secret hygiene:** No OAuth client secret, access token, refresh token or account key is bundled. Do not commit, share or paste the supplied JSON. If the secret has been exposed to unintended audiences, rotate it in Google Cloud Console.

**Verification sequence:** structure test → local `tools/list` → Windows sign-in → `gcp_project_describe` succeeds → available tool calls. A ZIP in Dropbox or Library is not evidence of runtime activation.
