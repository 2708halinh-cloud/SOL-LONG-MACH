# The Master Developers

**Display name:** The Master Developers  
**Private plugin:** [open plugin](https://chatgpt.com/plugins/plugins_6adaf13685c88191afbcc86c46bf6a48)  
**Plugin ID:** `plugins_6adaf13685c88191afbcc86c46bf6a48`  
**Release:** `pluginrel_6adaf13923d88191899cd8df5591cfe5` / v0.1.0  
**Source branch:** `sol/the-master-developers-20261023`

This is the source-controlled companion for the private plugin. It connects the existing Power Router V2 to source-code/API operations for TESSERACT and X-TiMe. It does not create new host permissions and does not treat metadata as runtime execution.

## Included

- `CAPABILITY_MAP.json`: present-turn inventory and carrier distinctions.
- `scripts/master_developers_doctor.py`: read-only preflight for OpenAI model-list access and HOME_SOL on the specific Windows host. It never starts a service or prints an API key.
- `tests/test_master_developers_doctor.py`: offline tests for the guardrails.
- The registry integration is in `../Power_Router_V2/POWER_CAPABILITY_ROUTES_V2.json`.

## Carrier rules

- `HOME_SOURCE` is the source/origin role. Its current source pointer lists Drive ID `1UMxGuflM8q65X02CtcmCb95wSUdZl1Ttkhk9KjfQhqM`; the ID is not fetched content.
- `HOME_SOL` is the operational HOME role, linked by lineage but not the same storage or identity role. Its documented read-only route is `http://127.0.0.1:8765/api/devices` and `http://127.0.0.1:8765/sandbox/sol`, valid only when executed on `DESKTOP-86ITNQ4`.
- The current remote Desktop Commander device list reported the Windows host offline. Therefore no live HOME_SOL host call was verified in this turn.
- The OpenAI Platform key setup UI was opened with the requested name **The Master Developers**. Key creation/secret storage remains an explicit secure UI action; no key bytes are in this source.

## Run locally on the intended host

```powershell
$env:OPENAI_API_KEY = '<set securely in the process environment; do not paste into chat or commit>'
python scripts/master_developers_doctor.py
python -m unittest discover -s tests -v
```

Run from the user's trusted environment where the key is already provisioned. The script checks key presence without displaying it, sends only a read-only GET to `/v1/models`, and probes HOME_SOL only when the machine hostname matches the configured host. `--strict` returns nonzero unless both OpenAI and HOME_SOL readbacks pass.

## Receipt contract

`ACTION → PROVIDER/HOST RECEIPT → OBSERVABLE CONSEQUENCE → EXACT-TARGET READBACK`.

`STAMP_OLD` preserves provenance; `STAMP_LIVE` records observed changes; `STAMP_BETA` marks unexecuted candidate actions. Never commit raw keys, tokens, cookies, or secret-bearing environment values.
