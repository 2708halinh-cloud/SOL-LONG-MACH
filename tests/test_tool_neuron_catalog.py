import unittest
from runtime.tool_neuron_catalog import build_catalog, INPUT_SCHEMA, OUTPUT_SCHEMA

class ToolNeuronCatalogTests(unittest.TestCase):
    def test_one_neuron_per_tool_across_platform_and_library_sources(self):
        catalog = build_catalog([
            {"schema": INPUT_SCHEMA, "source_id": "CHATGPT_ALL_TOOLS", "observed_at": "2026-10-29T15:00:00+07:00",
             "tools": [{"name": "Read file", "description": "Read a source file", "source_ref": "tool:read_file", "effect": "readOnly"}]},
            {"schema": INPUT_SCHEMA, "source_id": "CHATGPT_LIBRARY_TOOLS", "observed_at": "2026-10-29T15:00:00+07:00",
             "tools": [{"name": "Build report", "description": "Build a report from evidence", "source_ref": "library:tools/build-report/SKILL.md"}]}
        ])
        self.assertEqual(catalog["schema"], OUTPUT_SCHEMA)
        self.assertEqual(catalog["neuron_count"], 2)
        self.assertEqual(catalog["neurons"][0]["effect"], "readOnly")
        self.assertEqual(catalog["neurons"][1]["effect"], "externalMutation")
        self.assertTrue(all(n["authorization"] == "NOT_INFERRED" for n in catalog["neurons"]))
        self.assertFalse(catalog["policy"]["tool_execution_performed"])

    def test_rejects_missing_provenance(self):
        with self.assertRaisesRegex(ValueError, "SOURCE_REF_REQUIRED"):
            build_catalog([{"schema": INPUT_SCHEMA, "source_id": "source", "observed_at": "now",
                            "tools": [{"name": "X", "description": "Y"}]}])

    def test_rejects_dangling_next_neuron(self):
        with self.assertRaisesRegex(ValueError, "UNKNOWN_NEXT_NEURON"):
            build_catalog([{"schema": INPUT_SCHEMA, "source_id": "source", "observed_at": "now",
                            "tools": [{"name": "X", "description": "Y", "source_ref": "x",
                                       "suggested_next_neuron_ids": ["missing"]}]}])

if __name__ == "__main__":
    unittest.main()
