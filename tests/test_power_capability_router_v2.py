"""Exercises SOL capability-routing choices without pretending connectors executed."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / (
    "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/"
    "OS_WORK/tools/_Plugins/power_capability_router.py"
)
spec = importlib.util.spec_from_file_location("power_capability_router_v2", SOURCE)
router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(router)


class PowerCapabilityRouterTests(unittest.TestCase):
    def check_route(self, term, target):
        result = router.route(term, ROOT)
        self.assertIn(target, [x["capability_id"] for x in result["candidates"]])
        self.assertEqual(result["entrypoint"], "_Plugins")
        self.assertEqual(result["return_to"], "_Plugins")
        self.assertTrue(result["cycle_closed_by_metadata"])
        self.assertFalse(result["action_executed"])
        self.assertIsNone(result["provider_receipt"])
        self.assertIsNone(result["readback"])
        self.assertTrue(all(not x["provider_callable_verified_this_run"]
                            for x in result["candidates"]))
        self.assertNotEqual(result["next_action"], "OPEN")

    def test_master_skill(self):
        self.check_route("The Master Flatform tạo Agent Skill", "master-flatform")

    def test_ggdv_template(self):
        self.check_route("GGDV Template Creator provenance", "ggdv-template-creator")

    def test_x_time(self):
        self.check_route("X-TiMe Multi-Agent AI Platform", "x-time-multi-agent")

    def test_generative_ai(self):
        self.check_route("Công cụ AI tạo sinh", "generative-ai")

    def test_azure(self):
        self.check_route("Azure DevOps pipelines", "azure-devops")

    def test_call_tools(self):
        self.check_route("Call_Tools phi năng lực", "call-tools")

    def test_smithery(self):
        self.check_route("smithery.ai MPC toolbox", "smithery-mpc")

    def test_brightdata(self):
        self.check_route("brightdata browser", "brightdata-browser")

    def test_github(self):
        self.check_route("Github sửa repository", "github")

    def test_tomorrow(self):
        self.check_route("Tomorrow.io Weather", "tomorrow-weather")

    def test_storage_sync(self):
        self.check_route("Dropbox đồng bộ ChatGPT Library", "storage-sync")

    def test_unknown_keeps_concrete_discovery(self):
        item = router.route("Một khả năng chưa định danh trong bộ định tuyến", ROOT)
        self.assertEqual(item["candidates"], [])
        self.assertEqual(item["next_action"], "DISCOVER_SKILLS_AND_PROVIDER_CAPABILITIES")
        self.assertEqual(item["return_to"], "_Plugins")
        self.assertEqual(item["never_terminal_label_only"], "OPEN_REQUIRES_NEXT_ACTION")

    def test_refuse_empty_task(self):
        with self.assertRaises(ValueError):
            router.route("", ROOT)


if __name__ == "__main__":
    unittest.main()
