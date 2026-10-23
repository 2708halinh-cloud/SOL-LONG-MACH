# SOL MCP Cloud Gateway — bootstrap

**Status:** source bootstrap only. This directory does not claim that a VPS, public HTTPS endpoint, or upstream connector is already live.

## Why this lives here
This is an additive deployment unit in `2708halinh-cloud/SOL-LONG-MACH`. It does not replace `LOCAL_BRIDGE/`, existing runtime files, or the existing ChatGPT MCP connections. Keep upstreams independently identifiable and preserve source receipts.

## Planned topology

```
Project MCP client
  -- HTTPS + Bearer token -->
Caddy (TLS) --> SOL MCP Gateway (/mcp)
                  |-- GitHub REST (read-only)
                  |-- Chroma HTTP API (read-only heartbeat)
                  |-- Azure DevOps REST (read-only project listing)
                  |-- Google Drive API (read-only listing)
                  |-- LOCAL_BRIDGE (explicit HTTPS/tailnet URL)
                  '-- Android bridge (explicit HTTPS/tailnet URL)
```

The local PC and Android are not made public by this service. Connect them through a private overlay or an authenticated outbound tunnel; do not expose ADB or the local bridge directly to the Internet. A bridge is considered connected only after its health endpoint responds.

## Required deployment inputs

- A reachable VPS with Docker Compose and a DNS name.
- DNS A/AAAA record pointing to the VPS and inbound TCP 80/443 permitted.
- `MCP_BEARER_TOKEN`: long random secret, provided through VPS secret/environment management.
- `GITHUB_TOKEN`: fine-grained token with **Contents: read-only** for only the intended repository.
- `CHROMA_URL`: trusted Chroma endpoint; no write tools are exposed.
- `AZDO_ORG` and `AZDO_PAT`: PAT scoped to project read only.
- `GOOGLE_DRIVE_ACCESS_TOKEN`: short-lived OAuth access token with least-privilege Drive read scope; rotate it. Prefer a managed OAuth refresh flow before production.
- `LOCAL_BRIDGE_URL` and `ANDROID_BRIDGE_URL`: optional trusted HTTPS endpoints reachable from VPS. Do not use a device's RFC1918 address unless VPS has a private route to it.

Never commit `.env`, access tokens, OAuth client secrets, SSH private keys, or service-account JSON. The gateway does not read the user's local credential files or reuse ChatGPT connector credentials.

## Deploy

1. Provision a VPS. The existing Hostinger API inventory was empty at bootstrap time; the previously seen Moind VM `SOL-X66-MAY-AO` was stopped, network-blocked, 256 MB RAM / 1 GB disk, and is not an appropriate public HTTPS host without re-provisioning.
2. Point a DNS name at the VPS.
3. Clone this branch, create a private `.env` on the VPS from `.env.example`, and set secrets there.
4. Set `MCP_DOMAIN` to the DNS name, then run `docker compose up -d --build`.
5. Verify `https://$MCP_DOMAIN/healthz`, then run an MCP Streamable HTTP handshake/list-tools test against `https://$MCP_DOMAIN/mcp` using the Bearer token.
6. Verify each upstream tool independently. A gateway health response is not proof that upstream services are connected.

## Current limitations

- No VPS was provisioned or modified by this bootstrap because no usable VPS appeared in the checked Hostinger accounts.
- No DNS/domain or certificate was configured.
- GitHub, Chroma, Azure DevOps, Drive, local bridge, and Android bridge credentials/URLs must be supplied at runtime.
- The Drive adapter uses a runtime access token and therefore requires token rotation/refresh operations to be established separately.
- Only read-only diagnostic/list operations are included. No shell, arbitrary URL fetch, ADB command, file write, or deployment mutation tool is exposed.

## Readback contract

Record the VPS ID, deployment commit SHA, DNS/TLS result, gateway health result, MCP initialize/list-tools result, and per-upstream receipts before marking the service live. Any missing edge remains `OPEN`, not successful.
