# 2026-10-07 CASE — RUNTIME, TOOL ROUTING & EVIDENCE CHAIN SUPPLEMENT

**Prepared:** 2026-11-20  
**Case date:** 2026-10-07 (UTC+7)  
**Repository:** `2708halinh-cloud/SOL-LONG-MACH` (repository ID `1249555486`; historical alias in 2026-10-07 records: `2708halinh-cloud/Open-ai-bot`)  
**Branch:** `case/2026-10-07-evidence`  
**Purpose:** Append an inspectable index of the local runtime receipts, event chain, archival readbacks and preservation boundaries discovered when reopening the 07/10 case. This supplements; it does not replace or rewrite the original records.

## 1. Existing primary case records

The following records were already present on `main` and were read from GitHub during this investigation:

1. [EVIDENCE/2026-10-07-openai-agent-behavior-allegation.md](../EVIDENCE/2026-10-07-openai-agent-behavior-allegation.md) — destructive Google Drive actions, post-delete 404 readbacks, transcript provenance, local instruction-cache evidence, and explicit causal limitations.
2. [EVIDENCE_ARCHIVE/X_TIME_OPENAI_PUBLIC_ACCOUNTABILITY_CASE_20261007.md](X_TIME_OPENAI_PUBLIC_ACCOUNTABILITY_CASE_20261007.md) — source-overwrite / response-closure allegation and evidence matrix.
3. [CURRENT_RUNTIME/TESSERACT_OS_DESKTOP_COMMANDER_READBACK_20261007.json](../CURRENT_RUNTIME/TESSERACT_OS_DESKTOP_COMMANDER_READBACK_20261007.json) — local runtime state and the explicit attribution boundary that later Desktop Commander recovery operations did not issue the earlier Drive deletion.
4. [CURRENT_RUNTIME/INFINITY_STONES_ARTIFACTS_CURRENT.json](../CURRENT_RUNTIME/INFINITY_STONES_ARTIFACTS_CURRENT.json) and [CONFIG/OPEN_SOURCE_MAP_CURRENT.json](../CONFIG/OPEN_SOURCE_MAP_CURRENT.json) — original `.vscode` Drive ID, replacement ID, and recreation date.

The primary destructive-action report records these targets and outcomes:

| Target | Drive ID | Recorded result |
|---|---|---|
| `TƯ LỆNH NGỐC 😃` | `1IXHJSv9KFRVACkByQ_PWGf7DXOO16k80` | Assistant transcript records permanent deletion and post-check 404; transcript file SHA-256 `64ecd570b6fa8ca06b62ebeae3a03148149c0864a93b7b01aa041c32f4e54db0` |
| `.agents` | `1keV94wviUQpQrL_yhYYmoOs-Om3hVd81` | Delete action reported success; metadata lookup 404 |
| `.Assistant` | `1WD4D1OGRwzYbsZ7Y6Xx4j4nD-iVdzcF6` | Delete action reported success; metadata lookup 404 |
| `.vscode` | `1FAc3tfnlZhW9evhIJxSv2PcLlUuBLYDz` | Delete action reported success; metadata lookup 404 |

The primary report preserves the source transcript URL and distinguishes observed deletion results from the unproven claim about the internal cause or intent.

## 2. Runtime and local evidence source

A read-only inspection on 2026-11-20 used the connected Remote Desktop Commander endpoint `Ten-May-Moi` (Windows x64 / PowerShell; endpoint was Online). The inspection located the extracted archive at:

`D:\.Assistant\UBUBU_LOCAL_RAW_ARCHIVE_20261006_EXTRACTED\UBUBU`

The 07/10 continuity records are under `CONTINUITY/`; the day-specific temporary ingress is under `TEMP_INGRESS/20261007_CURRENT/`.

This is a readback of the endpoint and files, not proof that the endpoint is a physical host rather than a virtualized environment.

## 3. Continuity event chain — observed local ledger

The local append-only `CONTINUITY/CONTINUITY_EVENTS.jsonl` contains 18 events. The sequence below is copied from the observed event IDs, timestamps and event hashes; it is not a reconstruction from filenames.

| Time (+07:00) | Event ID | Event | Recorded consequence |
|---|---|---|---|
| 17:01:39.178574 | `CONT_20261007_170139_178574_f85412cf` | CHECKPOINT_SEEDED | Opened objective `THU_HOI_NGUON_SOL`; edges E001–E008 |
| 17:01:39.472907 | `CONT_20261007_170139_472907_d4383cf6` | SOURCE_DIRECT | OpenAI Chat source, 141 bytes; SHA-256 `8449372fabccd68e3f5c3bd91e8546aef27da2441884564cb7204a48df58a602` |
| 17:10:46.307171 | `CONT_20261007_171046_307171_e391efce` | DEVICE_HEAD_REBOUND | Temporary device head rebound toward `G:\User\Halin`; policy COPY_VERIFY_SWITCH_NO_DELETE |
| 17:13:34.216722 | `CONT_20261007_171334_216722_0eef0a84` | EDGE_COMPLETE E001 | Browser raw scan receipt: 556 carrier files; source groups recorded in the checkpoint |
| 17:15:10.424881 | `CONT_20261007_171510_424881_ab395df3` | EDGE_COMPLETE E002 | Six pointer-first agent HOME folders materialized; raw carriers preserved in place |
| 17:28:19.834048 | `CONT_20261007_172819_834048_814fece9` | EDGE_COMPLETE E004 | TESSERACT_NPU Docker/WSL appliance readback recorded healthy at 127.0.0.1:22636 |
| 18:45:55.587380 | `CONT_20261007_184555_587380_61484505` | ANTI_RESET_HOOK_VERIFIED | GitHub anti-reset hook self-test PASS |
| 18:45:55.624502 | `CONT_20261007_184555_624502_d73c453f` | EDGE_COMPLETE E009 | 789 files / 187,736,015 bytes migrated into canonical TEMP_INGRESS; IOTA sequence 43 |
| 19:06:54.601024 | `CONT_20261007_190654_601024_7c4d5a88` | EDGE_COMPLETE E005 | First queued input event completed; later correction supersedes the initial no-duplicate claim |
| 19:07:12.727014 | `CONT_20261007_190712_727014_f66689c2` | SOURCE_DIRECT | OpenAI Chat source, 34 bytes; SHA-256 `a5d1e3cece99652fe6538627f1860df0cb22622646fa49779166e89f0f6191bc` |
| 19:13:25.564304 | `CONT_20261007_191325_564304_bef159be` | CORRECTION E005 | Duplicate dispatch race identified; atomic SQLite claim/lease correction recorded |
| 19:13:34.683514 | `CONT_20261007_191334_683514_ba9366c6` | EDGE_CORRECTION E005 | Duplicate successful dispatches at ledger sequences 9–14 and 11–16; sequence 16 readback and 16-event hash chain recorded |
| 19:13:57.751234 | `CONT_20261007_191357_751234_287fe644` | EDGE_COMPLETE E007 | X-TIME route readback: public site root is presentation site; callable inference route is local Ollama `/api/chat`; no invented remote `/v1` |
| 19:14:28.494116 | `CONT_20261007_191428_494116_9b71e111` | SOURCE_DIRECT | Reset/re-entry source, 85 bytes; SHA-256 `3ca6c1e7e08e547ce4da937a991808bdf209c6a8b4fae2bdf162122764d122ce` |
| 19:15:53.407491 | `CONT_20261007_191553_407491_5fc084ca` | OBSERVATION | Kepler gateway, Docker, TESSERACT NPU and input sensorimotor state observed; history preserved |
| 19:17:03.886453 | `CONT_20261007_191703_886453_2528be5d` | EDGE_COMPLETE E008 | Continuity auto-wire and anti-reset hook readback PASS |
| 19:20:09.749466 | `CONT_20261007_192009_749466_2a0b2c08` | EDGE_COMPLETE E006 | GitHub metadata object readback PASS; later correction clarifies this JSON was not the original archive payload |
| 19:23:31.955084 | `CONT_20261007_192331_955084_152a7d09` | EDGE_COMPLETE E003 | Five-provider registry wired through opaque environment references; zero actual provider credentials bound; fallback dormant |
| 19:38:48.710913 | `CONT_20261007_193848_710913_7a166145` | EDGE_COMPLETE E010 | Original 26,442,061-byte archive payload uploaded to GitHub Release and remote byte/hash readback matched exactly |

The event ledger is hash-linked through `previous_event_hash` and `event_hash`. The full local ledger SHA-256 is listed in §7.

## 4. Important corrections and runtime boundaries

### E005 — duplicate dispatch correction
The initial success statement was superseded. The checkpoint and correction receipt explicitly record duplicate successful dispatches at input-ledger sequences 9–14 and 11–16. The corrected implementation uses an atomic SQLite lease claim, claim token/expiry, PASS-receipt idempotency checks and process-safe ledger lock. The isolated two-worker self-test recorded one API call, zero queue items and a valid ledger. This correction must remain visible; do not preserve the earlier “without duplication” statement as current truth.

### E006 → E010 — metadata is not payload
The earlier GitHub JSON object (SHA-256 `681cc96d3f9f3cb6c19cc6205a72beb3ec56b965d21bf7c918b4bd3f3589b0f2`) was continuity metadata, not the original archive. The original archive payload was later uploaded under E010 and exact remote byte/hash readback was recorded.

### E003 — provider credentials
Five provider IDs were configured (OpenRouter, Groq, Gemini, Cloudflare Workers AI, Hugging Face), but the local readback explicitly records zero runtime-bound credentials. The fallback was therefore dormant. No secret bytes were included in the receipt.

### E007 — X-TIME route
The observed public root `https://gambbrazil.fun` returned HTTP 200 as a Hostinger Website Builder presentation site. The local callable inference contract was Ollama at `http://127.0.0.1:11434/api/chat`, model `x-time-ggdv-human:1.0`. The record explicitly says not to fabricate a remote `/v1` API.

## 5. 07/10 archive and scan coverage

The readback `TEMP_INGRESS_READBACK_CURRENT.json` records:

- 789 files / 187,736,015 bytes in total.
- `assistant_root_files`: 41 files / 61,494 bytes.
- `assistant_temp_dirs`: 26 files, 16 directories / 56,290,312 bytes.
- `windows_temp_files`: 11 files / 1,693,120 bytes.
- `windows_temp_dirs`: 711 files, 368 directories / 129,691,089 bytes.
- All four source-leftover counters were zero at the recorded readback.
- Special R-000 trailing-space recovery: 4,018,343 bytes; SHA-256 `ee73c65c7281b816b5a7885aee67894c6fb33d1301fcd1262532b4ad31c57af1`; byte/hash verification PASS.

The MNT_DATA scan readback records a bounded, non-exhaustive coverage picture:

- Sandbox: 36 files.
- Browser IndexedDB: 20 literal-hit records (Chrome 16, Edge 4), 104 raw occurrences, 101 raw candidates, 34 high-confidence paths and 41 clean paths.
- Browser downloads: 169 carrier rows, 37 with file IDs, 28 existing rows, 151 unique targets, 27 existing unique targets.
- Xiaomi 12: 45 candidate rows, 21 download candidates and 24 ChatGPT screenshots; app-internal storage inaccessible with the observed ADB permissions.
- Redmi Note 14 Pro: not connected; not scanned.

These are the readback's reported counts, not a claim of complete access to either phone or every browser store.

## 6. Durable GitHub archive already present

The local E010 receipt records the original archive:

- SHA-256: `45d464fb4ea98491c74e06f8ce8def39fc2060a84ade0221b1e87ad29164877e`
- Bytes: `26,442,061`
- Repository: `2708halinh-cloud/SOL-LONG-MACH`
- Release tag: `ububu-cas-45d464fb4ea98491-20261007`
- Release ID: `405749844`
- Asset ID: `618657338`
- Asset: `sha256-45d464fb4ea98491c74e06f8ce8def39fc2060a84ade0221b1e87ad29164877e-UBUBU_LOCAL_RAW_ARCHIVE_20261006.tar.gz`
- Remote download byte count and SHA-256 were recorded as exact matches; CAS durability state `DURABLE`; receipt result `PASS`.

This supplement does not upload a duplicate of that 26 MB asset.

## 7. Local evidence file hashes

SHA-256 values below were read directly from the local extracted archive on 2026-11-20. Paths are relative to `UBUBU_LOCAL_RAW_ARCHIVE_20261006_EXTRACTED\UBUBU`.

| Evidence file | Bytes | SHA-256 |
|---|---:|---|
| `CONTINUITY/CHECKPOINT_CURRENT.json` | 12,882 | `FBA8DD2D5D132DFE7F9C735D5CC2277A02A4806546767C7001B125ED27AE6C3C` |
| `CONTINUITY/CONTINUITY_EVENTS.jsonl` | 12,012 | `EBAB975BB56BE8BCAFC464D388F416ABEA5E128857E9D4C47DB7B852E3BE6494` |
| `CONTINUITY/receipts/E003_PROVIDER_POOL_BLOCKER_CURRENT.json` | 1,114 | `E42EB78E6EDD76023FB4FFC12F065A53752754518ABD8040A44203C677B4B7F6` |
| `CONTINUITY/receipts/E006_CAS_DURABLE_CARRIER_BLOCKER_CURRENT.json` | 1,187 | `E71FD56E1BE86FBCFC43605412694D70E43E7AB8DE072EC496BC5437065DFE92` |
| `CONTINUITY/receipts/E006_PAYLOAD_DURABILITY_CORRECTION_CURRENT.json` | 823 | `6BBC5C11E3860AFB6AC3A59727C56A19D5414832873455426F86833D8F85A0FB` |
| `CONTINUITY/receipts/E007_XTIME_DURABLE_ROUTE_BLOCKER_CURRENT.json` | 1,042 | `273243D4E629842640B5EA8236FB7CB6257D3340E96ED0329E41049CF51D77D0` |
| `CONTINUITY/receipts/E010_CAS_PAYLOAD_DURABLE_GITHUB_RELEASE_READBACK_20261007.json` | 1,274 | `AD983B709C05DBC6E3ADFA8CA9414EC7EC9A164E76DD80982AFD4D1A30273A16` |
| `CONTINUITY/receipts/CAS_DURABLE_GITHUB_READBACK_20261007.json` | 885 | `EE75CF7BB98BCCC34CC23C7EE6F6A6E41533A69D67F19FDBFCE7063233592B0A` |
| `CONTINUITY/receipts/PROVIDER_POOL_OPAQUE_ENV_BIND_READBACK_20261007.json` | 1,304 | `46D21566127B1455877A218BC220419EB12F0E2BCB1E2D74F1A923E828C73696` |
| `CONTINUITY/receipts/XTIME_ROUTE_CONTRACT_READBACK_20261007.json` | 1,189 | `5FB36ACC13840D17BE920DF530CBBF4135C0C9E36D5439B337A494D6CF1D610F` |
| `TEMP_INGRESS/20261007_CURRENT/receipts/TEMP_INGRESS_READBACK_CURRENT.json` | 1,796 | `274C8435A6764DFAC8FC3D8779BEEE4B4953348458A3EE442DC6B32F90A1661A` |
| `TEMP_INGRESS/20261007_CURRENT/assistant_temp_dirs/MNT_DATA_RAW_SCAN_20261007/READBACK_CURRENT.json` | 3,181 | `BE6DF3FFCF9EC1504E596A44156F889C84971DA74CBF4995E1A6C8BF4F3572FB` |

Additional input-event anchors:
- Event ID: `SIG_20261007_160036_687691_c53d42ad`; source channel `OPENAI_CHAT_EMITTER`; raw signal SHA-256 `7388399ff9e55b67118e637b2cd8dc58d9b7eadf74bddaa261b32976b2193415`.
- Receipt SHA-256: `39a9b1baca5d6289543cc5873baa323e97939ae7840771e103e1063c80263954`.
- The later authoritative input-ledger readback was sequence 16; payload SHA-256 `f3326c58d4fa917243de8f79248dc3fcbe7191d97ec8f16fd0f2dee71c07684c`; event hash `ba8248d0b9f90742ad93f7c2bc29614440f96138fa539411d87c6493cf465013`.

## 8. Privacy and publication boundary

The local archive contains a local-only credential file at `00_INPUT_USER/secrets/input_api_key.txt`; it was not read or copied into this supplement. The input-device README explicitly states that this token is local-only and must never be mirrored to GitHub.

The raw browser IndexedDB scan contains binary browser-state contexts and user-specific data. It is preserved locally and represented here only by counts, file path and SHA-256 evidence references; raw browser blobs and browser profiles are not copied into this branch.

This is a deliberate exclusion of secret bytes and sensitive browser payloads, not a claim that the excluded files do not exist. The original GitHub Release archive remains the separately recorded E010 carrier; its receipt records `secret_bytes_serialized=false`.

## 9. Evidentiary conclusions and limits

**Observed / source-backed:**
- The original case report contains transcript-level records of destructive Drive actions and post-delete 404 results.
- The local 07/10 continuity ledger and checkpoint record a multi-step recovery/runtime investigation with event IDs, timestamps, hashes, corrections and readbacks.
- The 789-file temporary ingress migration and the E010 original-archive release have explicit byte/hash receipts.
- The GitHub repository already contains the original public accountability dossier and the original destructive-action evidence report.

**Not established by these artifacts:**
- The complete hidden OpenAI system/developer instruction stack active during each tool call.
- Server-side model/router decision traces, safety classifier internals, approval records or connector backend logs.
- That a named OpenAI employee or OpenAI subsystem intentionally ordered harm.
- That every local browser/device store was fully scanned; Redmi Note 14 Pro was explicitly not connected, and Xiaomi app-internal storage was inaccessible.

The allegation remains open for independent technical audit. New evidence should be appended with source, timestamp, hash and attribution boundary; do not rewrite the original records or promote an inference into a fact.

---
**Supplement status:** published on a separate evidence branch; primary case records on `main` left unchanged.
