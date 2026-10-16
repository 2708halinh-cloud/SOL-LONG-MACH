import json
import tempfile
import unittest
from pathlib import Path
from runtime.tesseract_agent_boot import CONFIG, evaluate

LIVE_REPO = Path(__file__).resolve().parents[1]

class BootRoutesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "CONFIG_SOL").mkdir()
        (self.root / "AGENTS.md").write_text("SOURCE_A", encoding="utf-8")
        self.dev = self.root / "mock_dev"
        self.dev.mkdir()
        (self.dev / "device0").write_text("NEVER_OPEN", encoding="utf-8")
        self.cfg = json.loads((LIVE_REPO / CONFIG).read_text(encoding="utf-8"))
        self.save()

    def save(self):
        (self.root / CONFIG).write_text(json.dumps(self.cfg), encoding="utf-8")

    def test_contune_missing_is_open_not_fabricated(self):
        out = evaluate(self.root, self.dev)
        self.assertIn("AGENTS_CONTUNE_MD_NOT_FOUND", out["open_edges"])
        self.assertFalse(out["plus"]["exists"])
        self.assertFalse((self.root / "AGENTS_CONTUNE.md").exists())

    def test_exact_contune_and_fresh_main(self):
        a = evaluate(self.root, self.dev)
        (self.root / "AGENTS.md").write_text("SOURCE_B", encoding="utf-8")
        (self.root / "AGENTS_CONTUNE.md").write_text("PLUS", encoding="utf-8")
        b = evaluate(self.root, self.dev)
        self.assertNotEqual(a["agent"]["sha256"], b["agent"]["sha256"])
        self.assertTrue(b["plus"]["exists"])
        self.assertNotIn("AGENTS_CONTUNE_MD_NOT_FOUND", b["open_edges"])

    def test_dev_is_metadata_only(self):
        before = (self.dev / "device0").read_bytes()
        out = evaluate(self.root, self.dev)
        self.assertEqual(out["hands"]["device_metadata"]["entry_count"], 1)
        self.assertFalse(out["device_bytes_read_or_written"])
        self.assertFalse(out["usb_writer_invoked"])
        self.assertEqual((self.dev / "device0").read_bytes(), before)

    def test_reject_escape_and_writes(self):
        self.cfg["tac_nhan"]["source_path"] = "../outside"
        self.save()
        with self.assertRaises(ValueError):
            evaluate(self.root, self.dev)
        self.cfg["tac_nhan"]["source_path"] = "AGENTS.md"
        self.cfg["hands"]["writes_to_dev"] = True
        self.save()
        with self.assertRaises(ValueError):
            evaluate(self.root, self.dev)

    def test_shared_hands_and_azure_toolset_are_fresh_read(self):
        """The boot actually reads both manifests rather than trusting the config labels."""
        for key, value in (
            ("route_manifest", "TAY-OLD"),
        ):
            target = self.root / self.cfg["tools_gateway"][key]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(value, encoding="utf-8")
        azure = self.cfg["tools_gateway"]["azure_devops_toolset"]
        for k, value in (("source", "# Toolset\n### Core\n"), ("index", "{}"), ("read_only_router", "# offline router\n")):
            target = self.root / azure[k]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(value, encoding="utf-8")
        a = evaluate(self.root, self.dev)
        self.assertTrue(a["tools_gateway"]["manifest"]["exists"])
        self.assertTrue(a["tools_gateway"]["azure_devops"]["toolset"]["exists"])
        self.assertTrue(a["tools_gateway"]["azure_devops"]["index"]["exists"])
        self.assertFalse(a["tools_gateway"]["azure_devops"]["executed"])
        self.assertFalse(a["tools_gateway"]["azure_devops"]["provider_connected"])
        self.assertNotIn("AZURE_DEVOPS_TOOLSET_SOURCE_NOT_FOUND", a["open_edges"])
        manifest = self.root / self.cfg["tools_gateway"]["route_manifest"]
        manifest.write_text("TAY-NEW", encoding="utf-8")
        b = evaluate(self.root, self.dev)
        self.assertNotEqual(a["tools_gateway"]["manifest"]["sha256"], b["tools_gateway"]["manifest"]["sha256"])

    def test_unsafe_azure_toolset_pointer_rejected(self):
        self.cfg["tools_gateway"]["azure_devops_toolset"]["index"] = "../outside"
        self.save()
        with self.assertRaises(ValueError):
            evaluate(self.root, self.dev)

    def test_agents_missing_keeps_open(self):
        (self.root / "AGENTS.md").unlink()
        out = evaluate(self.root, self.dev)
        self.assertEqual(out["status"], "OPEN_AGENTS_SOURCE")

if __name__ == "__main__":
    unittest.main()
