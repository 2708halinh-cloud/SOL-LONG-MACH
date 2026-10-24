# TESSERACT FrankenMoE — Mixtral preparation

Branch: `mixtral`. This is a reproducible starter, not a built model; no weights or credentials are included.

## Preconditions
Resolve every placeholder to an actual model repository and immutable revision. Confirm license, architecture, tokenizer, base-model lineage, and the exact MergeKit-MoE configuration schema/version before loading weights. Agent/provider labels are not model repository IDs.

## Build sequence
1. Pin MergeKit version and every model revision.
2. Run `python validate_config.py` and review all provenance.
3. Estimate RAM/VRAM and disk needs; sparse routing reduces active compute but does not guarantee all experts fit in memory.
4. Install the verified upstream MergeKit-MoE version and run `mergekit-moe mergekit-moe.yml ./artifacts/frankenmoe --verbose`.
5. Save build logs, config SHA-256, source revisions/hashes, output manifest, exit code, and held-out routing evaluations.

The starter intentionally fails preflight until model IDs are verified. Positive/negative prompts provide gate-training examples; validate hidden-state extraction with the exact pinned tokenizer and prompt template. Add an abstain route and evaluate on held-out SQL records. Validate schema and provenance independently of model routing; never execute generated SQL without independent authorization and policy checks.

On memory pressure: stop new jobs, reduce concurrency, checkpoint resumable work, and preserve source artifacts and the journal. Do not allow untrusted model output to erase durable state.
