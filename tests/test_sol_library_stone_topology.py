"""Prevent the forbidden SPACE workspace root without erasing a routed source sibling."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "CHATGPT_LIBRARY" / "SOL LONG MẠCH - HẬU THIÊN TĨNH"
CORE = LIB / "COMPUTER_KHÍ💜BRAIN_OS_POWER"
SPACE = CORE / "EARTH_PEOPLE_XƯƠNG🔵THỦY_SPACE"


class LibraryStoneTopologyTests(unittest.TestCase):
    def test_canonical_library_roots_and_no_space_workspace_sibling(self):
        directories = {p.name for p in LIB.iterdir() if p.is_dir()}
        self.assertTrue(
            {"COMPUTER_KHÍ💜BRAIN_OS_POWER", "OS_WORK"}.issubset(directories)
        )
        # This sibling is a real routed carrier: OS_WORK/brainwave_logger.py
        # resolves DEFAULT_DIR from its parent to BRAIN_WAVE_LOGS.
        self.assertIn("BRAIN_WAVE_LOGS", directories)
        logger = (LIB / "OS_WORK" / "brainwave_logger.py").read_text(encoding="utf-8")
        self.assertIn('DEFAULT_DIR = ROOT / "BRAIN_WAVE_LOGS"', logger)
        self.assertFalse((LIB / "SPACE_STONE_WORKSPACE").exists())

    def test_computer_five_stones_and_one_agents(self):
        self.assertEqual({p.name for p in CORE.iterdir()},
            {"AGENTS.md", "BRIDGE_TIME_TÓC🟢MỘC_TIME",
             "CORE_PLACES_INDEX_MÁU_🔴_HỎA_REALITY",
             "EARTH_PEOPLE_XƯƠNG🔵THỦY_SPACE",
             "INBOX_INPUT_PROJECTS_DA🟡KIM_MIND",
             "MEMORY_ARCHIVE_THỊT🟠THỔ_SOUL"})

    def test_memory_archive_has_no_parallel_root_and_routes_to_existing_executors(self):
        # An archive created at repository root repeats the exact structural
        # error observed on 2026-10-20, even when its script itself is valid.
        root_aliases = [p.name for p in ROOT.iterdir()
                        if p.is_dir() and p.name.casefold().startswith(("memory_achive", "memory_archive"))]
        self.assertEqual(root_aliases, [], "Do not create a second memory archive at repo root")
        soul = CORE / "MEMORY_ARCHIVE_THỊT🟠THỔ_SOUL"
        reg = json.loads((soul / "FORMAT_REGISTRY.json").read_text(encoding="utf-8"))
        self.assertEqual(reg["canonical_branch"], soul.relative_to(ROOT).as_posix())
        for key in ("executor", "inspect_readonly_companion"):
            path = ROOT / reg[key]
            self.assertTrue(path.is_file(), "Broken archive tool pointer: " + key)
            self.assertEqual(path.parent, LIB / "OS_WORK" / ".sandbox-bin")
        for format_name in ("ALL", "7Z", "BZ2", "GZ", "JAR", "LR", "RAR", "TAR", "XZ", "ZIP"):
            self.assertTrue((soul / format_name).is_dir(), format_name)

    def test_all_eight_moved_space_files(self):
        names = ["README.md","RESET_REENTRY_EVIDENCE_GATE_20261016.md","SOL_TOPOLOGY_PLANETS_SPACES_PATHS_SURFACES_POINTS_CARRIERS_5D_20261016.md","SPACE_MAP.json","SPACE_STONE_DROPBOX_SPACE_2026-10-16_04.md","SPACE_STONE_GITHUB_SPACE_2026-10-16_03.md","SPACE_STONE_GOOGLE_CLOUD_SPACE_2026-10-16_05.md","SPACE_STONE_WORKSPACE.code-workspace"]
        for name in names:
            self.assertTrue((SPACE / name).is_file(), name)
        data = json.loads((SPACE / "SPACE_MAP.json").read_text(encoding="utf-8"))
        self.assertEqual(data["workspace_folder"], SPACE.relative_to(ROOT).as_posix())
        self.assertIn("SPACE_STONE_WORKSPACE", data["legacy_workspace_folder"])

    def test_boot_and_time_do_not_route_to_deleted_space_root(self):
        boot = (ROOT / "runtime" / "tesseract_agent_boot.py").read_text(encoding="utf-8")
        time = (CORE / "BRIDGE_TIME_TÓC🟢MỘC_TIME" / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("HẬU THIÊN TĨNH/SPACE_STONE_WORKSPACE/", boot)
        self.assertIn("EARTH_PEOPLE_XƯƠNG🔵THỦY_SPACE/SOL_TOPOLOGY_PLANETS", boot)
        self.assertIn("../EARTH_PEOPLE_XƯƠNG🔵THỦY_SPACE/", time)


if __name__ == "__main__":
    unittest.main()
