# SSN NPU Runtime (reference implementation)
This package provides source-bound semantic candidate neurons, exponential Leaky Integrate-and-Fire decay, task-boundary reset, sparse synaptic adjacency, bounded Hebbian updates, explicit action gating, and a Vertex/Fragment/Render pipeline.

**Execution boundary:** semantic similarity only ranks candidates. It cannot authorize side effects. The host must explicitly approve execution, allow the risk class, provide all required fields, and bind a verified adapter.

**Backend:** this is a deterministic Python CPU reference, not a physical NPU/GPU implementation. Embedding encoder and real tool adapters are injected by the host. numpy.dot alone does not prove GPU execution.

Files: runtime/ssn_npu/core.py, runtime/ssn_npu/config/runtime.json, tests/test_ssn_runtime.py, skills/ssn-npu-runtime/SKILL.md.

Verify: `python -m unittest discover -s tests -v`.

The sparse matrix supports hundreds/thousands of directed edges without dense N×N allocation. The existing plugin has nine skill folders. This package does not fabricate additional skill records or claim that all source skills have been migrated. Load only verified catalog entries with capability_id, source_ref, risk, required fields, and adapter status.

Safe resource control means reducing concurrency/batch size at memory/thermal limits. Overclocking is disabled.
