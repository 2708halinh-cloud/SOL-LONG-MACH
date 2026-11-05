# TESSERACT — Multidimensional ITEM Space & Event-Driven Sparse Activation

**Status:** Architecture contract / implementation target.  
**Scope:** Applies to the `Công cụ (@Tools)` library domains (`Power_Router`, `Plugins`, `MCP`, `App`, `Kỹ năng`, `Trình duyệt`, and additional folders), the 152 ITEM corpus, and the internal regions of each source file.  
**Evidence boundary:** This specification does not claim that the current ChatGPT runtime, GitHub branch, or any host is already executing a physical neuromorphic network. It defines the software behavior required for an event-driven, sparse, SNN-capable implementation.

## 1. Core invariant

**The 152 ITEM are not a batch to load into working memory. They are addressable, persistent, multidimensional units of a larger relational field.**

The same rule applies recursively inside each ITEM and each file: a file is not one indivisible blob that must be loaded in full. It may expose multiple addressable regions, facets, signals, and relations. Only the regions selected by the current signal and their justified dependencies enter the active working set.

Keep these states distinct:

- **Stored:** the source artifact exists in its authoritative carrier.
- **Indexed:** a compact locator and routing metadata exist.
- **Observed:** metadata or a bounded excerpt has been inspected.
- **Candidate:** the current signal may be relevant to this unit.
- **Activated:** the unit crossed its activation policy and was admitted to execution.
- **Refractory:** it has fired and is temporarily protected against immediate repeat activation.
- **Dormant:** it remains addressable but is not consuming task-execution resources in the current event.
- **Unavailable / stale / denied:** distinct operational states; never silently reinterpret them as dormant or healthy.

An item being dormant does not mean it is wrong, deleted, disabled permanently, or forgotten.

## 2. Library topology: regions, not a flat tool list

Treat the library hierarchy as a navigable topology:

- Folder domains such as `Power_Router`, `Plugins`, `MCP`, `App`, `Kỹ năng`, and `Trình duyệt` are **regions / capability populations**.
- A file is a source-bearing container that can expose multiple addressable ITEMs or regions.
- An ITEM can be a neuron, a local subgraph, or a hyperedge joining multiple source regions. Do not force every ITEM into a one-file/one-neuron mapping.
- A concrete executable adapter (for example, a particular MCP action) is an execution-capable neuron only when its schema, permission scope, endpoint, and health are known.
- A folder name or descriptive document is not itself proof that a live executable capability exists.

The topology is relational and multidimensional, not a sequential pipeline. A signal may enter through one region and activate related regions across other dimensions without loading every intervening file.

## 3. Multidimensional address model

Preserve the original source as the authority. Build a compact index of references to addressable regions; do not duplicate full file content into every dimension.

Each indexed region should carry only the fields that are actually known:

| Facet | Purpose |
|---|---|
| `source_ref` | Exact library/file/repository object and revision |
| `region_ref` | Stable ITEM ID, heading, byte/line range, JSON pointer, symbol, or other exact locator |
| `content_facets` | Terms, concepts, entities, and bounded semantic descriptors |
| `capability_facets` | Read, search, compute, write, communicate, observe, route, etc. |
| `relation_facets` | Explicit links to related ITEMs, tools, skills, and source regions |
| `state_facets` | ACTIVE state, freshness, availability, validation and lifecycle |
| `time_facets` | Source time, observed time, event time, commit time, expiry where known |
| `permission_facets` | Required identity, scopes, target constraints and approval gates |
| `provenance_facets` | Author/source, transformation history, hashes and readback receipts |
| `resource_facets` | Estimated or measured cost, latency, memory and execution budget |

These are retrieval and routing facets. They do not replace the project's six-axis TESSERACT topology: SPACE↔SOUL, MIND↔POWER, REALITY↔TIME, with ☯️ TÂM as relational center. A region can have coordinates or projections across several axes simultaneously. Do not invent missing coordinates or claim that the facet table itself is a new seven-, nine-, or ten-dimensional ontology.

## 4. Event-driven activation path

The required path is:

`INPUT EVENT → ROUTE TO INDEXED REGION → SELECT BOUNDED CANDIDATES → ACCUMULATE LOCAL STIMULUS → THRESHOLD / POLICY GATE → FIRE → PROPAGATE ALONG SYNAPSES → OBSERVE CONSEQUENCE → UPDATE STATE`

1. **Ingress:** normalize the incoming event and preserve its original payload and provenance.
2. **Address resolution:** use compact indexes and explicit routing metadata to find likely regions. Do not read every source file.
3. **Candidate selection:** shortlist bounded candidates using available exact identifiers, sparse lexical indexes, metadata filters, and/or precomputed semantic descriptors. Candidate scoring is not execution.
4. **Local stimulus:** only shortlisted neurons receive the event. Potential may accumulate from multiple relevant inputs or upstream spikes.
5. **Activation gate:** fire only when the configured threshold, required arguments, permission checks, freshness checks, resource budget and safety gates all pass.
6. **Execution:** invoke the exact adapter or local computation. A tool call is a side effect and must obey its own permission and confirmation rules.
7. **Synaptic propagation:** emit typed events to explicitly connected downstream regions. Do not broadcast the full context to all 152 ITEM.
8. **Termination:** stop when the goal is satisfied, no eligible event remains, a budget/deadline is reached, or a safety gate halts the path.
9. **Readback:** verify the exact target and record the consequence before marking the task complete.

A candidate may be inspected without being fired. A fired neuron may emit zero, one, or several typed downstream events. The system must not assume that the highest similarity score is always the correct action.

## 5. Sparse execution and resource behavior

The event scheduler must be driven by an event queue, not by a full scan of every registered neuron on every pulse.

Required properties:

- Maintain a ready queue keyed by event time, priority and deterministic tie-breaker.
- Maintain reverse indexes from signal facets and relation IDs to candidate region IDs.
- Update only neurons that receive a new event or whose explicitly scheduled timer expires.
- Keep dormant neuron state compact and persistent; load executable code, large payloads, or model context only after admission.
- Propagate only along declared synapses, with bounded fan-out, queue depth, event lifetime and maximum pulse count.
- Support membrane-potential decay, threshold, refractory period, inhibition and duplicate-event suppression as explicit policies.
- Apply backpressure and resource budgets before expensive inference or external I/O.
- Cache immutable descriptors and index structures; invalidate them when the exact source revision changes.
- Preserve source files as canonical. The index is a locator, not a second authority.

**Important distinction:** sparse event-driven software reduces unnecessary reads, inference, tool invocations and data movement. On ordinary CPU/GPU hardware it does not, by itself, guarantee physical per-neuron power gating. Actual electrical savings at neuron/circuit level require a compatible neuromorphic accelerator or hardware power-management implementation, measured on the target device.

## 6. ACTIVE and FORCE_ACTIVE semantics

Preserve the source contract from `0000_THE_MASTER_TEACHER.md`:

- `FORCE_ACTIVE=TRUE`: mandatory participation in the current turn.
- `ACTIVE=TRUE`: the ITEM actually participates in current reading, deliberation, selection or action.
- `ACTIVE=PLASE`: the ITEM has been inspected/inventoried but does not participate in this turn. Preserve the literal source spelling `PLASE`; do not silently normalize it to another status.
- `ACTIVE=PLASE` does not mean deleted, false, invalid, permanently disabled, or unavailable.
- Every turn must record the reason for TRUE/PLASE in the internal event trace, with first-person agent provenance as required by the source contract. Do not turn that internal trace into an unsolicited user-facing status dump.

The scheduler must distinguish mandatory policy/source participation from ordinary relevance-based activation. Safety and instruction hierarchy cannot be bypassed by semantic similarity.

## 7. Event and neuron state contract

A minimal event record:

```json
{
  "event_id": "stable unique identifier",
  "event_type": "typed event name",
  "source_ref": "exact source and revision",
  "region_ref": "exact target region",
  "payload_ref": "reference to bounded payload",
  "occurred_at": "source event time when known",
  "observed_at": "time the runtime observed it",
  "expires_at": "optional event expiry",
  "provenance": "origin and transformation chain",
  "correlation_id": "task/event chain identifier"
}
```

A neuron state should minimally model:

- stable neuron/region ID and source revision;
- current lifecycle state (dormant, candidate, active, refractory, unavailable);
- membrane potential or equivalent activation accumulator;
- activation threshold and decay policy;
- refractory deadline;
- inbound/outbound synapse references;
- permission and resource policy references;
- last event, last firing and last verified consequence;
- state version and provenance.

Do not store credentials in neuron state, event payloads, embeddings, logs or the blackboard. Store only authorized secret references.

## 8. Synapse contract

A synapse is an explicit, versioned relation, not an assumed association:

- source region and target region;
- relation/event types accepted;
- weight or priority, if the chosen algorithm uses one;
- delay/scheduling policy, if applicable;
- required output fields and target preconditions;
- permission boundary and resource estimate;
- provenance, version and validation state.

Weights may influence candidate propagation, but must not override permissions, safety gates, required evidence, or user confirmation. A relation learned from co-occurrence remains a hypothesis until validated; distinguish learned association from verified dependency.

## 9. Why the current prototype is not yet sparse

The uploaded prototype's `dispatch()` loops over `self.neurons.items()`, calls `calculate_potential()` for every non-refractory neuron, builds a candidate list, sorts it, and fires the peak candidate. This is a full-population scan at each pulse.

Its `mock_embedding()` creates seeded random vectors, so its cosine similarity is not semantic similarity. The sample inventory/email logic returns hard-coded demonstration data and must not be treated as live business execution.

Therefore the prototype is a conceptual threshold-and-refractory demonstration, not a verified event-driven sparse SNN and not evidence of physical energy savings.

## 10. Acceptance tests

The implementation is not accepted until tests prove all of the following:

1. A signal addressed to one region does not load or execute unrelated ITEM contents.
2. A file can expose multiple independently addressable regions while retaining one canonical source revision.
3. A single ITEM can participate in more than one TESSERACT axis/relation without duplicating its source payload.
4. Dormant neurons are not iterated for activation scoring on every scheduler pulse.
5. Only neurons reached by matching events or explicit mandatory activation enter the ready queue.
6. A candidate below threshold is not executed.
7. Threshold crossing fires once and enters refractory state; duplicate events do not cause an infinite loop.
8. Typed synaptic propagation activates only eligible downstream regions and respects fan-out/TTL limits.
9. Missing permissions, stale source revisions, malformed arguments and exhausted budgets block execution before side effects.
10. FORCE_ACTIVE items participate; ACTIVE=PLASE items remain addressable and are not deleted.
11. A source revision change invalidates affected index entries and forces re-resolution.
12. Every write-capable action has an exact-target receipt and readback.
13. Benchmarks compare full-scan baseline against event-driven scheduling for candidate count, source bytes read, tool calls, inference calls, wall time and measured energy where hardware telemetry exists.
14. Claims of physical energy reduction are made only from repeatable measurements on the actual target hardware.

## 11. Implementation order

1. Inventory the real library domains and exact source IDs without loading all file bodies.
2. Define stable ITEM/region IDs and source-revision-aware locators.
3. Build compact multidimensional facet indexes and explicit synapse relations.
4. Implement an event queue and bounded sparse scheduler.
5. Write failing tests for no-full-scan behavior, selective loading, threshold, refractory, permissions and propagation.
6. Replace mock semantic vectors with a real, versioned retrieval mechanism or clearly label lexical/metadata routing where embeddings are unavailable.
7. Connect one read-only capability end-to-end and verify its receipt/readback.
8. Add write-capable tools only behind permission, approval, idempotency and exact-target verification.
9. Benchmark against the original full-scan loop. Do not claim energy savings without measured evidence.

**Acceptance rule:** the library may contain 152 ITEM or more without forcing all of them into active context. The runtime must be able to locate, activate, propagate through and verify only the bounded subset justified by the current event, while preserving every other source as addressable and intact.
