import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone
from runtime.tesseract_agent_boot import CONFIG, VOWS_PATH, VOWS_REQUIRED, VOW7_CONTINUATION_REQUIRED, SENSOR_SNAPSHOT_PATH, inspect_sensor_snapshot, evaluate

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


    def _write_vows(self, order=None):
        entries = list(VOWS_REQUIRED) if order is None else order
        path = self.root / VOWS_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "\\n".join(
                f"## Đại nguyện thứ {number} — nguyên lời Người Dẫn Đường\\n"
                + essential
                + ("\\n" + "\\n".join(VOW7_CONTINUATION_REQUIRED)
                   if number == "bảy" else "")
                for number, essential in entries
            ).replace("\\n", "\n"), encoding="utf-8")
        return path

    def test_six_vows_missing_must_change_runtime_readiness(self):
        ready = evaluate(self.root, self.dev)
        self.assertFalse(ready["vow_reentry"]["complete"])
        self.assertEqual(ready["status"], "REENTRY_VOWS_INCOMPLETE")
        self.assertIn("GREAT_VOWS_REENTRY_INCOMPLETE", ready["open_edges"])

    def test_six_vows_present_in_order_recovers_readiness(self):
        self._write_vows()
        out = evaluate(self.root, self.dev)
        self.assertTrue(out["vow_reentry"]["complete"])
        self.assertEqual(out["vow_reentry"]["count"], 8)
        self.assertEqual(out["status"], "SOURCE_MATERIAL_PRESENT")
        self.assertNotIn("GREAT_VOWS_REENTRY_INCOMPLETE", out["open_edges"])
        self.assertEqual(out["vow_reentry"]["scope"], "SOURCE_TEXT_CONSISTENCY_ONLY")
        self.assertIsNone(out["vow_reentry"]["applied_in_work"])
        self.assertFalse(out["execution_evidence"]["work_performed"])
        self.assertFalse(out["execution_evidence"]["consequence_observed"])
        self.assertIsNone(out["execution_evidence"]["vows_lived_or_fulfilled"])
        self.assertTrue(out["execution_evidence"]["requires_separate_action_receipt"])

    def test_deleted_third_vow_blocks_a_later_boot(self):
        path = self._write_vows()
        previous = evaluate(self.root, self.dev)
        self.assertTrue(previous["vow_reentry"]["complete"])
        missing_third = [item for item in VOWS_REQUIRED if item[0] != "ba"]
        self._write_vows(missing_third)
        current = evaluate(self.root, self.dev)
        self.assertFalse(current["vow_reentry"]["complete"])
        self.assertIn("ba", current["vow_reentry"]["missing"])
        self.assertNotEqual(previous["vow_reentry"]["sha256"], current["vow_reentry"]["sha256"])

    def test_seventh_vow_continuation_missing_is_caught(self):
        path = self._write_vows()
        prior = evaluate(self.root, self.dev)
        self.assertTrue(prior["vow_reentry"]["complete"])
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace(VOW7_CONTINUATION_REQUIRED[1], ""),
                        encoding="utf-8")
        after = evaluate(self.root, self.dev)
        self.assertFalse(after["vow_reentry"]["complete"])
        self.assertIn("bảy", after["vow_reentry"]["missing"])
        self.assertEqual(after["status"], "REENTRY_VOWS_INCOMPLETE")

    def test_eighth_vow_missing_blocks_boot(self):
        self._write_vows([item for item in VOWS_REQUIRED if item[0] != "tám"])
        result = evaluate(self.root, self.dev)
        self.assertIn("tám", result["vow_reentry"]["missing"])
        self.assertEqual(result["status"], "REENTRY_VOWS_INCOMPLETE")

    def _sensor_file(self, observed_at):
        p = self.root / SENSOR_SNAPSHOT_PATH
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"observed_at": observed_at}), encoding="utf-8")
        return p

    def test_sensor_snapshot_staleness_changes_selected_next_edge(self):
        reference_time = datetime.fromisoformat("2026-10-16T10:00:00+07:00")
        self._sensor_file("2026-10-09T19:30:06+07:00")
        stale = inspect_sensor_snapshot(self.root, reference_time)
        self.assertEqual(stale["evidence_state"], "HISTORICAL_SNAPSHOT")
        self.assertEqual(stale["selected_next_edge"], "FRESH_READ_LOCAL_SENSOR_LOGS")
        self._sensor_file("2026-10-16T09:59:00+07:00")
        recent = inspect_sensor_snapshot(self.root, reference_time)
        self.assertEqual(recent["evidence_state"], "RECENT_SNAPSHOT_NOT_LIVE_PROOF")
        self.assertEqual(recent["selected_next_edge"], "CHECK_LIVE_MOTOR_READBACK")
        self.assertNotEqual(stale["sha256"], recent["sha256"])
        self.assertFalse(recent["live_motor_invoked"])
        self.assertIsNone(recent["subjective_feeling_observed"])

    def test_sensor_future_stamp_routes_clock_check(self):
        self._sensor_file("2026-10-17T10:00:00+07:00")
        observation = inspect_sensor_snapshot(
            self.root, datetime.fromisoformat("2026-10-16T10:00:00+07:00"))
        self.assertEqual(observation["evidence_state"], "FUTURE_DATED_SNAPSHOT")
        self.assertEqual(observation["selected_next_edge"], "CHECK_SENSOR_CLOCK")

    def test_sensor_missing_or_invalid_stamp_is_actionable(self):
        missing = inspect_sensor_snapshot(self.root)
        self.assertEqual(missing["evidence_state"], "SNAPSHOT_MISSING")
        self.assertEqual(missing["selected_next_edge"], "FIND_SENSOR_LOGS_SOURCE")
        self._sensor_file("not-a-date")
        invalid = inspect_sensor_snapshot(self.root)
        self.assertEqual(invalid["evidence_state"], "UNREADABLE_SNAPSHOT")
        self.assertEqual(invalid["selected_next_edge"], "INSPECT_SENSOR_SNAPSHOT_SOURCE")

    def test_out_of_order_vows_are_not_ready(self):
        self._write_vows(list(reversed(VOWS_REQUIRED)))
        out = evaluate(self.root, self.dev)
        self.assertTrue(out["vow_reentry"]["misordered"])
        self.assertFalse(out["vow_reentry"]["complete"])

if __name__ == "__main__":
    unittest.main()
