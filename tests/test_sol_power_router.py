"""SOL Power Router: route actual source categories and always return to _Plugins."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / (
    "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/"
    "_Plugins/power_router.py"
)
spec = importlib.util.spec_from_file_location("sol_power_router", SRC)
power = importlib.util.module_from_spec(spec)
spec.loader.exec_module(power)


class PowerRouterTest(unittest.TestCase):
    def test_existing_manifest_and_metadata_back_edge(self):
        tools, idx, back = power.load(ROOT)
        self.assertEqual(len(idx["groups"]), 10)
        self.assertEqual(back["target"]["name"], "_Plugins")
        self.assertEqual(back["link_type"], "METADATA_POINTER_ONLY")
        self.assertTrue((tools / "_Plugins" / "power_router.py").exists())

    def test_real_source_paths_reachable(self):
        tools, index, back = power.load(ROOT)
        for group in index["groups"]:
            for source in group["sources"]:
                with self.subTest(group=group["id"], source=source):
                    self.assertTrue(power._safe(tools, source).exists(), source)

    def test_known_categories_choose_portal_and_return(self):
        examples = {
            "tìm kỹ năng": "skills",
            "máy chủ mcp": "mcps",
            "trình duyệt": "app_browser",
            "github PR": "devops",
            "webshare proxy": "network",
            "Dropbox đồng bộ": "storage",
            "sandbox python": "sandbox",
            "plugin kết nối": "plugins",
        }
        for task, expected in examples.items():
            with self.subTest(task=task):
                r = power.route(task, ROOT)
                self.assertEqual(r["selected_group"], expected)
                self.assertEqual(r["return_to"], "_Plugins")
                self.assertTrue(r["source_route_complete"])
                self.assertFalse(r["action_executed"])
                self.assertIsNone(r["live_provider_confirmed"])
                self.assertEqual(r["logical_traversal"][-1], "_Plugins_RETURN")

    def test_unknown_task_falls_back_to_skill_discovery(self):
        r = power.route("xyz nhiệm vụ chưa có nhóm", ROOT)
        self.assertEqual(r["selected_group"], "discovery")
        self.assertEqual(r["return_to"], "_Plugins")

    def test_input_required(self):
        with self.assertRaises(ValueError):
            power.route("  ", ROOT)

    def test_relative_escape_forbidden(self):
        tools, idx, back = power.load(ROOT)
        with self.assertRaises(ValueError):
            power._safe(tools, "../../../../../outside-root/secret.json")

    def test_wrong_back_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / power.ROOT_REL
            base.mkdir(parents=True)
            (base / power.CONFIG).parent.mkdir(parents=True, exist_ok=True)
            data = json.loads((ROOT / power.ROOT_REL / power.CONFIG).read_text(encoding="utf-8"))
            (base / power.CONFIG).write_text(json.dumps(data), encoding="utf-8")
            link = base / power.BACK
            link.parent.mkdir(parents=True)
            old = json.loads((ROOT / power.ROOT_REL / power.BACK).read_text(encoding="utf-8"))
            old["target"]["name"] = "NOT_PLUGINS"
            link.write_text(json.dumps(old), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "BACK_EDGE_NOT_SOURCE_POINTER"):
                power.load(root)


if __name__ == "__main__":
    unittest.main()
