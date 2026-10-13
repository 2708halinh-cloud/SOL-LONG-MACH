---
name: apify-sol-google-maps
description: Use for Apify Google Maps and Google Places crawling, extracting business/place data with compass/crawler-google-places Actor, inspecting inputs, running Apify jobs, and reading datasets through verified Apify MCP.
---
# Apify SOL — Google Maps

- Primary Actor (user-provided): `compass/crawler-google-places` / `nwua9Gu5YrADL7ZDj`.
- Use currently authenticated Apify MCP to fetch actor details and **its live input schema**; do not guess required input or claim a run when no tool receipt exists.
- Respect requested city, business category, number of results, language, fields and dataset target.
- Return run ID, run status, actual items count and source/dataset citation when available.
- Never fabricate Google Maps results. Actor execution may be billed; verify tool authorization and usage.
- If MCP is only configured but not connected, mark `RUNTIME_UNVERIFIED`, not `RUN_COMPLETE`.
