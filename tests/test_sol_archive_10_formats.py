"""Regression tests for the source-preserving archive classifier's external test adapters."""
import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "CHATGPT_LIBRARY" / "SOL LONG MẠCH - HẬU THIÊN TĨNH"
          / "OS_WORK" / ".sandbox-bin" / "sol_archive_10_formats.py")
spec = importlib.util.spec_from_file_location("sol_archive_10_formats", SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ReadOnlyExternalAdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def archive(self, name, magic):
        path = self.root / name
        path.write_bytes(magic + b"fixture-only-bytes")
        return path

    def assert_read_only_command(self, run_mock, expected_prefix, path):
        argv = run_mock.call_args.args[0]
        self.assertEqual(argv[:len(expected_prefix)], expected_prefix)
        self.assertEqual(argv[-1], str(path.resolve()))
        self.assertNotIn("x", argv)
        self.assertNotIn("e", argv)
        self.assertFalse(any(arg.startswith("-o") for arg in argv))
        self.assertFalse(run_mock.call_args.kwargs.get("shell", False))
        self.assertEqual(run_mock.call_args.kwargs["stdin"], mod.subprocess.DEVNULL)
        self.assertEqual(run_mock.call_args.kwargs["timeout"], 45)

    def test_7z_uses_test_mode_without_extracting(self):
        path = self.archive("fixture.7z", b"7z\\xbc\\xaf'\\x1c".encode("latin-1"))
        with patch.object(mod.shutil, "which", side_effect=lambda n: "/usr/bin/7zz" if n == "7zz" else None), \
             patch.object(mod.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as run:
            result = mod.inspect(path)
        self.assertEqual(result["detected"], "7Z")
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["adapter"], "7zz")
        self.assert_read_only_command(run, ["/usr/bin/7zz", "t", "-bd"], path)

    def test_rar_prefers_unrar_test_mode(self):
        path = self.archive("fixture.rar", b"Rar!\\x1a\\x07".encode("latin-1"))
        with patch.object(mod.shutil, "which", side_effect=lambda n: "/usr/bin/unrar" if n == "unrar" else None), \
             patch.object(mod.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as run:
            result = mod.inspect(path)
        self.assertEqual(result["detected"], "RAR")
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["adapter"], "unrar")
        self.assert_read_only_command(run, ["/usr/bin/unrar", "t", "-inul"], path)

    def test_lrzip_uses_test_mode_without_extracting(self):
        path = self.archive("fixture.lrz", b"LRZI")
        with patch.object(mod.shutil, "which", side_effect=lambda n: "/usr/bin/lrzip" if n == "lrzip" else None), \
             patch.object(mod.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as run:
            result = mod.inspect(path)
        self.assertEqual(result["detected"], "LR")
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["adapter"], "lrzip")
        self.assert_read_only_command(run, ["/usr/bin/lrzip", "-t"], path)

    def test_missing_adapter_is_explicit_and_does_not_execute(self):
        path = self.archive("fixture.7z", bytes.fromhex("377abcaf271c"))
        with patch.object(mod.shutil, "which", return_value=None), \
             patch.object(mod.subprocess, "run") as run:
            result = mod.inspect(path)
        self.assertEqual(result["status"], "NEEDS_ADAPTER")
        self.assertEqual(result["error_code"], "ADAPTER_NOT_FOUND")
        run.assert_not_called()

    def test_timeout_is_classified_without_exception_handler_failure(self):
        path = self.archive("fixture.7z", bytes.fromhex("377abcaf271c"))
        with patch.object(mod.shutil, "which", side_effect=lambda n: "/usr/bin/7z" if n == "7z" else None), \
             patch.object(mod.subprocess, "run", side_effect=subprocess.TimeoutExpired(cmd="7z", timeout=45)):
            result = mod.inspect(path)
        self.assertEqual(result["status"], "FAILED_SAFE")
        self.assertEqual(result["error_code"], "TimeoutExpired")

    def test_unsafe_zip_member_is_rejected_during_inspection(self):
        path = self.root / "unsafe.zip"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("../escape.txt", "fixture")
        result = mod.inspect(path)
        self.assertEqual(result["status"], "FAILED_SAFE")
        self.assertEqual(result["error_code"], "ValueError")
        self.assertFalse((self.root / "escape.txt").exists())

    def test_sources_are_not_extracted_or_written_by_inspection(self):
        path = self.archive("fixture.7z", bytes.fromhex("377abcaf271c"))
        before = path.read_bytes()
        with patch.object(mod.shutil, "which", return_value=None):
            result = mod.inspect(path)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse(result["extraction_performed"])
        self.assertFalse(result["sensitive_data_copied"])


if __name__ == "__main__":
    unittest.main()
