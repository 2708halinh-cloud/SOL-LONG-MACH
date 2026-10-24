import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent

class StarterContractTests(unittest.TestCase):
    def test_contract_has_provenance_and_abstention(self):
        import json
        contract = json.loads((ROOT / "routing_contract.json").read_text(encoding="utf-8"))
        self.assertIn("source_sha256", contract["record_required_fields"])
        self.assertEqual(contract["policy"]["low_route_confidence"], "ABSTAIN")
        self.assertEqual(contract["policy"]["missing_provenance"], "STOP_FORWARD")

    def test_template_contains_both_prompt_polarities(self):
        import yaml
        config = yaml.safe_load((ROOT / "mergekit-moe.yml").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(config["experts"]), 2)
        for expert in config["experts"]:
            self.assertTrue(expert["positive_prompts"])
            self.assertTrue(expert["negative_prompts"])

if __name__ == "__main__":
    unittest.main()
