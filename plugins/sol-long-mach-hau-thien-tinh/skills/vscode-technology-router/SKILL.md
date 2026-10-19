---
name: vscode-technology-router
description: Route CONFIG_SOL/GGDV_RUNTIME developer-technology requests for remote exploration, run/debug, source control, extensions, testing, Google Cloud Data Agent Kit, Google Cloud, Metal, containers, Microsoft Edge and Chrome using live provider status and readback.
---
# VS CODE / DEVELOPER TECHNOLOGY ROUTER

## Requested capability names
Normalize these user-facing labels without changing their intent:
- KHÁM PHÁ TỪ XA → REMOTE_EXPLORATION
- CHẠY VÀ GỠ LỖI → RUN_DEBUG
- QUẢN LÝ MÃ NGUỒN → SOURCE_CONTROL
- TIỆN ÍCH MỞ RỘNG → EXTENSIONS
- KIỂM TRA → TESTING
- DATA AGENT KIT → GOOGLE_CLOUD_DATA_AGENT_KIT
- GOOGLE CLOUD → GOOGLE_CLOUD
- METAL → APPLE_METAL
- CONTAINERS → CONTAINERS
- MICROSOFT EDGE TOOL → MICROSOFT_EDGE_TOOL
- CHORME TOOL / CHROME TOOL → CHROME_TOOL

## Provider discipline
For each capability, resolve fresh runtime state before action:
`DECLARED → PROVIDER_DISCOVERY → AUTH/CONNECTION → CALLABLE → ACTION → READBACK`.

Never infer `CONNECTED` from a config line. Never equate a generic browser automation provider with Chrome/Edge DevTools. Never equate OpenAI sandbox containers with the user's local Docker/Podman runtime.

## Current known provider classes
- Remote filesystem/terminal: Remote Desktop Commander when an authorized device is connected.
- Source control: GitHub tools when authenticated/callable.
- ChatGPT plugin/skill extension management: Plugin Management / Plugin Creator; this is distinct from VS Code extension installation.
- Testing and isolated execution: current OpenAI container/Python runtime where appropriate; remote/local target tests require the target runtime.
- Google Cloud Data Agent Kit: external Google Cloud technology supporting VS Code/VS Code-compatible IDEs and coding-agent plugins/MCP; live Google Cloud credentials/provider must be separately connected.
- Google Cloud data plane: use exact provider connectors when available; Google Drive is not a substitute for Google Cloud services.
- Apple Metal: requires a compatible Apple/macOS/Xcode runtime for actual execution; config presence is not runtime proof.
- Containers: distinguish ChatGPT sandbox container from user/device Docker/Podman/Kubernetes runtime.
- Edge/Chrome: exact DevTools/runtime provider must be discovered; cloud browser automation is a separate capability.

## Fallback rule
If an exact provider is absent, keep `DECLARED_OPEN` and route through SOL Capability Forge for discovery/forge. Do not fabricate a live bridge.
