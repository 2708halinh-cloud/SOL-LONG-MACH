"""Administrator System's × Toolset project-bound integration tests."""
import unittest
from pathlib import Path
from runtime.administrator_toolset import preflight, select

ROOT = Path(__file__).resolve().parents[1]

class AdministratorToolsetTests(unittest.TestCase):
    def test_project_admin_and_source_toolset(self):
        result = preflight(ROOT)
        self.assertTrue(result["source_checks_passed"])
        self.assertEqual(result["azure_source_routes"], 97)
        self.assertEqual(result["azure_source_tools"], 44)
        self.assertEqual(result["azure_source_categories"], 9)
        self.assertEqual(result["semantic_families"], 9)
        self.assertEqual(result["project_role"], "Administrator System's — SOL PROJECT ONLY")
        self.assertFalse(result["actual_provider_admin_granted"])
        self.assertFalse(result["remote_azure_action_executed"])

    def test_toolset_routes_do_not_impersonate_live_provider(self):
        result = select(ROOT, "Truy xuất danh mục dự án và nhóm dự án")
        self.assertEqual(result["return_to"], "_Plugins")
        self.assertFalse(result["toolset_as_live_mcp_inferred"])
        self.assertFalse(result["actual_provider_admin_granted"])
        self.assertEqual(result["governance_decision"], "ACTION_NOT_YET_EXECUTED")
        self.assertTrue(result["capabilities"])

    def test_missing_repository_does_not_fabricate_activation(self):
        with self.assertRaisesRegex(ValueError, "SOURCE_ABSENT_OR_OUTSIDE_REPOSITORY"):
            preflight(Path("/nonexistent/administrator-toolset"))

if __name__ == "__main__":
    unittest.main()