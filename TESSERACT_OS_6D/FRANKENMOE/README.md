# TESSERACT FrankenMoE — Mixtral branch preparation

## Objective
Prepare a reproducible, evidence-backed path to a sparse Mixture-of-Experts (MoE) build using MergeKit-MoE, with hidden-state routing initialized from positive/negative prompt sets. This branch does not contain model weights or credentials.

## Branch
`tesseract/mixtral-frankenmoe-20261025`

## Important compatibility rule
All experts must share a compatible architecture/tokenizer and the expected base-model lineage for the selected MergeKit-MoE recipe. Provider labels or agent IDs are not Hugging Face model IDs. Resolve each requested model to an actual repository/revision and license before building. Do not substitute a model by guessing.

## Files
- `mergekit-moe.yml`: starter configuration; replace explicit `REPLACE_WITH_VERIFIED_MODEL_ID` values with verified model repositories/revisions.
- `routing_contract.json`: data contract for SQL records, prompt evidence, and route decisions.
- `validate_config.py`: offline validation for required fields, unresolved placeholders, positive/negative prompt presence, and memory budget settings.
- `requirements.txt`: minimum Python dependencies for config validation. MergeKit itself is installed separately according to its upstream installation instructions.

## Build sequence
1. Verify model IDs, revisions, licenses, tokenizer and architecture compatibility.
2. Pin the MergeKit version and model revisions; keep source hashes and config hash in the build receipt.
3. Run the config validator before loading weights.
4. Estimate total host RAM/VRAM and disk requirements. Quantization, offloading, and expert count must be selected from measured available resources; MoE reduces active expert computation but does not automatically eliminate storage/residency costs.
5. Run `mergekit-moe mergekit-moe.yml ./artifacts/frankenmoe --verbose` in an isolated environment after replacing placeholders and installing the verified upstream version.
6. Record command, exit code, logs, output manifest, model revision IDs, SHA-256 hashes, and evaluation results.
7. Evaluate routing quality on held-out SQL examples, including an abstain/unknown route. Do not route solely from untrusted natural-language prompts or SQL text; apply SQL schema validation and policy checks independently.

## Resource safety
Do not enable automatic deletion or destructive rollback based only on an untrusted model output. On memory pressure, stop new jobs, reduce concurrency, checkpoint resumable work, and preserve source artifacts and journal integrity.
