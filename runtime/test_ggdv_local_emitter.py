import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ggdv_local_emitter import emit_from_packet, verify_local_evidence


class LocalEmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.provider = self.root / "provider.txt"
        self.target = self.root / "target.txt"
        self.provider.write_text("provider action receipt", encoding="utf-8")
        self.target.write_text("readback target bytes", encoding="utf-8")
        digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        self.packet = {
            "type": "OP_RESULT",
            "input_open": True,
            "history_checked": True,
            "history_refs": ["local-test:historical-source"],
            "source_refs": ["local-test:authorized-source"],
            "executed": True,
            "provider_receipt_ref": str(self.provider),
            "target_readback_ref": str(self.target),
            "readback_matches_expected": True,
            "evidence_files": {
                "provider": {"path": str(self.provider), "sha256": digest(self.provider)},
                "target": {"path": str(self.target), "sha256": digest(self.target)}
            },
            "text": "readback target bytes"
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_file_bytes_allow_emission(self):
        emitted = []
        self.assertTrue(emit_from_packet(self.packet, self.root, emitted.append))
        self.assertEqual(emitted, [self.packet["text"]])

    def test_generated_prose_cannot_replace_source_bytes(self):
        packet = dict(self.packet)
        packet["text"] = "Đã hoàn tất mọi công việc theo nhận định của mô hình"
        emitted = []
        self.assertFalse(emit_from_packet(packet, self.root, emitted.append))
        self.assertEqual(emitted, [])

    def test_changed_target_bytes_suppress_emission(self):
        self.target.write_text("changed contents", encoding="utf-8")
        emitted = []
        self.assertFalse(emit_from_packet(self.packet, self.root, emitted.append))
        self.assertEqual(emitted, [])

    def test_forged_receipt_string_is_not_proof(self):
        packet = dict(self.packet)
        packet.pop("evidence_files")
        self.assertFalse(verify_local_evidence(packet, self.root))
        self.assertFalse(emit_from_packet(packet, self.root, lambda _: None))

    def test_ref_cannot_escape_authorized_root(self):
        external = self.root.parent / (self.root.name + "-external")
        external.write_text("outside", encoding="utf-8")
        try:
            packet = dict(self.packet)
            packet["provider_receipt_ref"] = str(external)
            packet["evidence_files"] = dict(self.packet["evidence_files"])
            packet["evidence_files"]["provider"] = {
                "path": str(external), "sha256": hashlib.sha256(external.read_bytes()).hexdigest()
            }
            self.assertFalse(verify_local_evidence(packet, self.root))
        finally:
            external.unlink()

    def test_local_host_cli_invokes_gate(self):
        packet_path = self.root / "response_packet.json"
        packet_path.write_text(json.dumps(self.packet, ensure_ascii=False), encoding="utf-8")
        cmd = [sys.executable, str(Path(__file__).with_name("ggdv_local_emitter.py")),
               "--packet", str(packet_path), "--receipts-root", str(self.root)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), self.packet["text"])
        self.target.write_text("different", encoding="utf-8")
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")

    def test_dialogue_keeps_t003_without_file_receipts(self):
        packet = {"type": "DIALOGUE", "input_open": True, "text": "Đây là ý kiến cá nhân."}
        emitted = []
        self.assertTrue(emit_from_packet(packet, self.root, emitted.append))
        self.assertEqual(emitted, [packet["text"]])

    def test_available_action_beats_progress_report(self):
        packet = dict(self.packet)
        packet.update(type="OP_PROGRESS", callable_action_available=True)
        emitted = []
        self.assertFalse(emit_from_packet(packet, self.root, emitted.append))
        self.assertEqual(emitted, [])


if __name__ == "__main__":
    unittest.main()
