---
name: google-cloud
description: Use the user-owned Google Cloud MCP on the Windows SOL control plane to inspect GCP projects, Cloud Storage buckets, Cloud Run services, Compute Engine VMs and enabled APIs. Activate for requests mentioning Google Cloud, GCP, gcloud, cloud project configuration, cloud IAM diagnostics, or cloud resource inspection.
compatibility: Windows host with Python 3 and Google Cloud SDK; local VS Code MCP over stdio. Google sign-in requires a separate interactive OAuth authorization.
metadata:
  version: "0.1.0"
  project: "alert-tiger-508618-h7"
---
# Google Cloud — SOL Windows MCP

This skill routes **Google Cloud** tasks through the local MCP server defined in `../../../.vscode/mcp.json`, launched on the Windows control plane. Use the configured project `alert-tiger-508618-h7` as an intended project ID, **not** proof the signed-in account can access that project.

## Run / verify

1. Verify the installed `gcloud` CLI on **Windows** and whether a Google account is authenticated. If not, use `gcloud auth login` with interactive Google OAuth; do not capture authorization codes in chat.
2. Verify project access using `gcloud projects describe alert-tiger-508618-h7 --format=json` or the `gcp_project_describe` MCP tool. Mark access **UNVERIFIED** until an actual response succeeds.
3. Use MCP `gcp_status`, `gcp_projects_list`, `gcp_storage_buckets_list`, `gcp_run_services_list`, `gcp_compute_instances_list`, `gcp_enabled_apis_list` only for their declared read-only behavior.
4. Preserve source facts, identity, project, path, action result and readback. Don't claim a Cloud API, ChatGPT Plugin or Windows process is connected just because the config files exist.
5. For writes (IAM changes, API enabling, Cloud Run deploys, bucket creation), use an explicitly approved operation via an authenticated tool; this bundled server intentionally does not expose generic shell or mutable tools.

## OAuth client file

The user's `client_secret_…apps.googleusercontent.com.json` is an OAuth desktop client configuration, **not** a service-account key and not an access token. The MCP server uses `gcloud`'s already-authenticated local user identity, so the client-secret JSON is not copied into the skill. For ADC-based client libraries only, `gcloud auth application-default login --client-id-file=PATH` is a separate optional interactive step that can overwrite an existing local ADC session.

## Boundaries

- Windows controls; Android is an endpoint. Dropbox is optional transport, not the source of project truth.
- ChatGPT's cloud Plugin is a distinct registration and identity. The local `.vscode/mcp.json` does not install a ChatGPT Plugin.
- Keep credentials out of GitHub, Library, logs, environment dumps, command-line arguments and shared output.
- `192.168.1.42:8080` is a proposed LAN address, not a Google Cloud API endpoint.

See `references/OPERATIONS.md` for entrypoints, transport distinctions and troubleshooting.
