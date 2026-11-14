# Tools → Neurons: source-bound integration

This folder is the repository mirror of the ChatGPT Library Tools area. The neuron materializer lives at runtime/tool_neuron_catalog.py.

## Pipeline

1. Take a fresh, explicit inventory of platform-callable tools and a separate inventory of Library Tools/Skills.
2. Store each inventory as JSON using the TOOL_NEURON_INVENTORY_TEMPLATE.json schema. Each record must preserve its source reference and observation time.
3. Run:
   python runtime/tool_neuron_catalog.py platform-tools.json library-tools.json --output build/TOOL_NEURON_CATALOG_CURRENT.json
4. Load the generated descriptors into the Swift TesseractNeuronRuntime. Dendrites ranks semantic similarity, Soma delegates to a real provider adapter, Axon returns output and suggested next-neuron IDs.
5. Verify each provider adapter independently. A catalog record is not proof that a connector is installed, authenticated, authorized, or currently reachable.

## Effect policy

Only an explicitly observed read-only tool may be marked readOnly. Missing or unknown effect defaults to externalMutation and is blocked by the Swift runtime unless a caller explicitly opts in. Provider adapters must still enforce the actual authorization boundary.

## Provenance and scope

- Do not merge platform tool inventory with Library source inventory; preserve source_id, source_ref, and observed_at.
- Do not infer provider IDs or permission grants from a display label or skill name.
- This pipeline transforms metadata into neuron descriptors. It does not move/uninstall ChatGPT plugins, alter account-level connectors, or execute any tool during catalog generation.
- The local Intel Driver & Support Assistant report at file:///G:/OS_Workspace/Detailed-System-Report.html is a separate read-only hardware evidence source. It must not be treated as a list of callable software tools or as authorization to control devices.
