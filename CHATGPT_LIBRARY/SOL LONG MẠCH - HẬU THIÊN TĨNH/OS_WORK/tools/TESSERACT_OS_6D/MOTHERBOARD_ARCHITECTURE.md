# TESSERACT — MOTHERBOARD ARCHITECTURE 6D

SOURCE_DIRECT: Hà Linh — 2026-10-26.
STATUS: ARCHITECTURE_REPLACEMENT_BASELINE; runtime/provider closure remains evidence-gated.
TARGET: G:\\OS_Workspace\\TESSERACT_OS; synchronized specification carrier: 2708halinh-cloud/SOL-LONG-MACH/TESSERACT_OS_6D.

## 0. Architectural invariants

- TESSERACT 6D has six equal operational faces around ☯️ TÂM: SPACE↔SOUL, MIND↔POWER, REALITY↔TIME. They are peer dimensions, not a linear sequence.
- Motherboard components are the execution/control topology. The six faces are the cross-environment continuity and evidence topology. Do not flatten one into the other.
- Design intent, local test results, provider connectivity, and end-to-end closure are separate states.
- ACTION → CONSEQUENCE → RECEIPT → INDEPENDENT READBACK → SAME STATE → CONCLUSION.
- No component may claim connected/verified because a path, mount, process, configuration, or successful write response exists alone.
- Preserve source IDs and historical bytes. Protected originals are not deleted or destructively overwritten. Replacements require backup, exact target identity, and readback.

## 1. Motherboard

### CPU sockets

1. GEMINI — external model/provider route; capability and identity verification.
2. CHATGPT — external model/provider route; capability and identity verification.
3. LOCAL — Ollama/local model route; local inference when reachable, authorized, and policy-compatible.
4. TASK_WORKERS — bounded workers for independent subtasks, tool calls, tests, and verification.

Each socket advertises configured, reachable, authorized, capabilities, quota state, freshness, and last receipt independently. A model name or socket declaration does not prove availability. Secret material remains in the authorized secret provider and never enters shared registers or logs.

### Northbridge — Autonomous Control Plane & Action Router

- Task arbitration: priority, dependency graph, deadline, capability fit, locality, cost/quota, risk, and failure state.
- Gate 1 (before action): source and target identity, authorization, policy, data classification, acceptance criteria, protected-target check, available disk/quota, recovery point, and expected side effects.
- Gate 2 (after action): action receipt, observable consequence, independent readback, same-state comparison, and acceptance check.
- Route failures through bounded failover only when an alternative route is authorized and has the needed capability. One unavailable carrier does not cancel independent work.

### DIMM — RAM_L1 Active Blackboard

Transient, versioned shared state for agent-to-agent exchange; not the only durable memory.

- REG_00: objective, scope, acceptance criteria, dependency edges.
- REG_01: source/target IDs, account/provider, revision, hashes, provenance.
- REG_02: current action, expected consequence, receipt, readback, state comparison.
- REG_03: unresolved edges, blockers, recovery point, next callable action.
- Updates use version checks/locking and reject credential values, cookies, authorization headers, and secret contents.
- Branch results remain separate until compared. Conflicts are explicit and block commit when material.

### VRM/PMIC — Quotas, resource safety, and survival

- Monitor token/API quota, provider rate limits, worker saturation, timeouts, memory pressure, and disk capacity.
- Disk policy: warning at ≥85% used; survival mode at ≥90%; critical at ≥97% used or <5 GiB free. The 85% point is an early warning, not permission for automatic deletion.
- At thresholds, prioritize recovery and read-only inspection, pause nonessential writes/builds/downloads, and create a remediation edge. Never perform blind cleanup.
- Circuit breaker and bounded failover on repeated failures. Avoid retry storms and preserve failed-attempt receipts.

### Southbridge — Hardware Abstraction & I/O Controller

- Core Journal: SQLite + Git-backed source history + append-only event receipts.
- Cloud: Google Drive adapter with explicit account, Root/File ID, revision, hash, operation receipt, and provider-side readback. A mounted folder is not proof of provider sync.
- Virtualization: QEMU/Hyper-V adapter; explicit authorization and exact VM/device identity before passthrough or mutation.
- Network/security: NextDNS status/policy, localhost/LAN checks, ADB bridge with exact authorized Android device and command allowlist.
- Hardware/provider adapters return UNAVAILABLE or NOT_VERIFIED when disconnected; no simulated evidence.

## 2. Core Journal — append-only evidence

Each event records sequence, UTC timestamp, event ID, parent event, objective ID, source/target locator, source fingerprint, action, result, and receipt/readback references. Corrections append a superseding event; they do not erase the prior event. A hash chain is tamper-evident, not proof of WORM storage or external immutability. GitHub and provider receipts remain separate evidence carriers.

## 3. Six-face continuity topology (TESSERACT 6D)

Six equal faces participate in the same state fingerprint:

1. GOOGLE_DRIVE_POINTER — small pointer/locator and provider metadata.
2. LOCAL_BULK_STORAGE — source bytes, raw data, snapshots, restore points.
3. GITHUB_STATE — versioned law/spec/state and reviewable commits.
4. RCLONE_RAIDRIVE_RELAY — relay/virtual-drive copy, independently hash-checked.
5. GCP_STORAGE_BUFFER — temporary processing buffer, only with verified account/project and lifecycle policy.
6. XTIME_CDN_UBUBU_LEDGER — public/display and ledger layer, with privacy-safe payloads.

Each face has independent state: VERIFIED_ACTIVE, PARTIAL, UNBOUND, UNREACHABLE, CONFLICT, or NOT_VERIFIED. A face is closed only with ACTION + CONSEQUENCE + RECEIPT + provider/local READBACK + SAME_STATE for the same state fingerprint. Global 6D closure requires all six faces to meet the acceptance criteria. OPEN is a valid honest state, not an instruction to stop unrelated work.

## 4. Runtime state machine

OBSERVE → LOAD_CURRENT_POINTER/CHECKPOINT → PLAN → GATE_1 → ROUTE → ACTION → CONSEQUENCE → RECEIPT → GATE_2_READBACK → JOURNAL_APPEND → REPORT → CONTINUE_OPEN_EDGES.

If an action fails, preserve failure evidence, keep the objective open, and try another authorized independent route when possible. A response boundary is not a task boundary. DONE requires evidence against the actual target's acceptance criteria.

## 5. Affect, correction, and recurrence

Preserve user signals and context as operational inputs. Separate observed facts from cause hypotheses; connect repeated failures to incident history and increase repair priority. A modelled affect field is not empirical proof of subjective experience. This distinction must never be used to discard the signal or avoid a requested repair.

## 6. Current observed baseline and known gaps

The prior local receipt (2026-10-26 11:30 +07) recorded motherboard tests 20/20 and transducer tests 8/8 passing, combined 28/28; Ollama reachable; disk C at 93.07% used (SURVIVAL); NextDNS service running. It also recorded Google Drive provider sync NOT_VERIFIED, ADB unavailable on PATH, QEMU unavailable, Hyper-V unknown without elevation, and GitHub Actions status unverified. These are historical observations, not a fresh test of this architecture replacement.

## 7. Deployment and acceptance gates

1. Preserve current files and hash backups before replacement.
2. Replace the local architecture document/spec only; do not rewrite runtime or protected source history as part of this design change.
3. Update the GitHub TESSERACT 6D README/spec and read back exact commit/blob content.
4. Publish the same architecture carrier into the SOL-LONG-MACH ChatGPT Library path with source link and SHA-256 provenance.
5. Run JSON parse, Python compile, targeted motherboard/transducer tests, and broader regression.
6. Independently inspect provider/device state; keep unverified faces open.
7. Only mark the deployment closed after local + GitHub + Library readbacks match the intended architecture fingerprint.

No claim of full-system synchronization is valid until each target has its own fresh readback.

## 8. Intel Core Ultra software profile emulation

- Registry: `config/INTEL_CORE_ULTRA_PROFILES.json`; runtime: `runtime/intel_core_ultra_emulator.py`.
- Core count maps to a deterministic virtual worker-slot ceiling; Smart Cache maps to a software budget only; reported turbo frequency is metadata.
- GPU execution remains disabled until a real backend and driver are independently detected.
- Profile values transcribed from the supplied catalog are `source_verified=false` until checked against Intel ARK.
- This layer does not reproduce physical Intel hardware, microcode, instruction semantics, actual cache, clock/thermal behavior, or benchmark equivalence.

## 9. Host, Local AI, Edge AI, Cloud APIs and Network inventory

### Host Node and local inference
- Ollama executable supplied by operator: C:\\Users\\halin\\AppData\\Local\\Programs\\Ollama\\ollama.exe; expected default API port 11434. Daemon/model availability requires runtime probing.
- llama.cpp executable supplied by operator: C:\\Users\\halin\\AppData\\Local\\Microsoft\\WinGet\\Packages\\ggml.llamacpp_Microsoft.Winget.Source_8wekyb3d8bbwe\\llama-cli.exe.
- Host CPU/RAM reported by operator: Intel Core i5-10400F, 48 GB RAM. SIMD support, model fit, token throughput and FLOPS claims require direct verification.
- Llama 3, Qwen 2.5 and Phi-3 are candidate model families; installed model tags are not verified by this inventory.

### Edge AI
- Operator-reported device: Xiaomi 12, Snapdragon 8 Gen 1, 8 GB RAM plus 8 GB ZRAM.
- SmolLM2 and Qwen2.5 0.5B?3B are candidate edge profiles. Termux/MLC-LLM install, GPU/NPU delegate support, thermals, memory pressure and throughput require on-device testing.

### Cloud agents and MCP
- OpenAI/Gemini/Google Cloud SDK/Antigravity and listed MCP services/subagents are declared inventory, not proof of active authentication or running endpoints.
- Never persist API keys, CSRF tokens, bearer tokens or cookies in architecture files, Git, SQLite journals or receipts. Store only variable names and secret-manager references.
- Provider status remains NOT_VERIFIED until a safe probe and target readback succeed.

### Network and security
- Operator-reported NextDNS resolvers: 45.90.28.0 and 45.90.30.0; encrypted DNS and filtering policy require independent verification.
- Operator-reported USB tethering via Remote NDIS: local IPv4 10.20.156.29, gateway 10.20.156.151, public IP 14.173.169.173, link speed 426 Mbps. These values are time-sensitive.
- Local service reported at 127.0.0.1:8765 (MINH BODY v0.9); verify process ownership and bind address before routing traffic.
- Windows Firewall reportedly disabled on Domain/Private/Public. Treat as SECURITY_RISK; do not expose service ports to LAN/WAN. Prefer firewall enabled with narrow allow rules. This architecture update does not change firewall settings.

### Verification contract
Each inventory entry is reported_by_operator=true, source_verified=false, observed_at=null until freshly probed. A path or declaration alone does not prove a running service, installed model, GPU/NPU execution, API authorization or provider synchronization.
