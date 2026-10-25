# Google Cloud: MCP / Tools / Plugin operational guide

## Local VS Code MCP

The VS Code MCP server identifier is **Google Cloud** and its config is `.vscode/mcp.json`. VS Code must open this bundle's root as the workspace or merge its `servers["Google Cloud"]` object into an existing workspace's `.vscode/mcp.json` without overwriting existing entries.

This server uses Python's standard library only. Google APIs are accessed using `gcloud`, with 7 explicitly enumerated read-only MCP tools. Communication stays on local stdio between VS Code and Windows. The account is selected by the existing gcloud CLI authentication state; this server cannot obtain OAuth consent automatically.

## Windows authentication

1. Install Google Cloud SDK if `gcloud` is absent: https://cloud.google.com/sdk/docs/install
2. Run `gcloud auth login` and complete Google consent in the Windows browser. Inspect project access with `gcloud projects describe alert-tiger-508618-h7`.
3. If Python application-default credentials are required later, keep the installed desktop client JSON in a private folder and run `gcloud auth application-default login --client-id-file="C:\path\to\client_secret_....json"`. **This does not authorize the gcloud CLI identity** and can replace current ADC credentials.
4. Google Cloud access depends on IAM and enabled APIs, not possession of a JSON client configuration.

## ChatGPT Cloud Plugin / remote MCP

This bundle **does not register** a ChatGPT Plugin. A ChatGPT remote MCP integration needs an authenticated HTTPS endpoint, a cloud-accessible MCP server, and user-initiated connection through Plugins UI. Do not expose the local stdio server directly on `0.0.0.0` or paste OAuth secrets into ChatGPT app configuration. Distinguish Google Drive connector access from GCP project IAM.

## Troubleshooting

- `gcp_status` shows no gcloud binary: install SDK in Windows and reopen VS Code to refresh PATH.
- CLI authenticated but resource calls denied: confirm selected Google identity IAM project role and enabled API; the client ID by itself grants no resource permissions.
- VS Code MCP missing: inspect `.vscode/mcp.json`, run `py -3 scripts\check_setup.py`, and restart server from VS Code MCP panel.
- OAuth account mismatch: sign out/change gcloud account via Google-hosted flow; never send tokens to chat.
- Windows offline in external remote tools: local VS Code MCP can still work *on Windows* independently of remote Desktop Commander.
