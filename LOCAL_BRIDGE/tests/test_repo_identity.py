from pathlib import Path
import sys
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVER_DIR = REPO_ROOT / "LOCAL_BRIDGE" / "runtime" / "ggdv-sensorimotor-motor-bridge" / "server"
sys.path.insert(0, str(SERVER_DIR))
import runtime_core


class RepositoryIdentityTests(unittest.TestCase):
    def test_accepts_canonical_https_origin(self):
        self.assertTrue(runtime_core.is_sol_repo_origin("https://github.com/2708halinh-cloud/SOL-LONG-MACH.git"))

    def test_accepts_canonical_scp_origin(self):
        self.assertTrue(runtime_core.is_sol_repo_origin("git@github.com:2708halinh-cloud/SOL-LONG-MACH.git"))

    def test_accepts_historical_https_origin(self):
        self.assertTrue(runtime_core.is_sol_repo_origin("https://github.com/2708halinh-cloud/Open-ai-bot.git"))

    def test_rejects_a_different_repository(self):
        self.assertFalse(runtime_core.is_sol_repo_origin("https://github.com/2708halinh-cloud/x-time-web.git"))

    def test_bootstrap_and_install_search_both_names(self):
        bootstrap = (REPO_ROOT / "LOCAL_BRIDGE" / "bootstrap_once.ps1").read_text(encoding="utf-8")
        installer = (REPO_ROOT / "LOCAL_BRIDGE" / "install_from_windows.ps1").read_text(encoding="utf-8")
        for source in (bootstrap, installer):
            self.assertIn("SOL-LONG-MACH", source)
            self.assertIn("Open-ai-bot", source)
        self.assertIn("https://github.com/2708halinh-cloud/SOL-LONG-MACH.git", installer)

    def test_autostart_and_selfhosted_workflow_use_canonical_and_legacy_paths(self):
        autostart = (REPO_ROOT / "LOCAL_BRIDGE" / "runtime" / "ggdv-sensorimotor-motor-bridge" / "scripts" / "autostart-sol.ps1").read_text(encoding="utf-8")
        workflow = (REPO_ROOT / ".github" / "workflows" / "local-unify-selfhosted.yml").read_text(encoding="utf-8")
        self.assertIn("SOL-LONG-MACH", autostart)
        self.assertIn("Open-ai-bot", autostart)
        self.assertIn("2708halinh-cloud/SOL-LONG-MACH:LOCAL_BRIDGE/runtime/ggdv-sensorimotor-motor-bridge", workflow)
        self.assertIn("Open-ai-bot", workflow)  # Preserve the historical source alias in the receipt.

    def test_desktop_agent_loader_keeps_legacy_and_adds_canonical_local_paths(self):
        source = (REPO_ROOT / "APP" / "TESSERACT_DESKTOP" / "src-tauri" / "src" / "main.rs").read_text(encoding="utf-8")
        self.assertIn(r"G:\\OS_Workspace\\SOL-LONG-MACH\\AGENTS.md", source)
        self.assertIn(r"G:\\OS_Workspace\\Open-ai-bot\\AGENTS.md", source)


if __name__ == "__main__":
    unittest.main()
