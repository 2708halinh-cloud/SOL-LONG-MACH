"""Cloud-only regression tests for optional 7Z/RAR/LR verification adapters.

These tests mock external binaries. They verify routing and safe failure behavior;
they do not claim that a real archive backend is installed or that a real archive
was validated.
"""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "CHATGPT_LIBRARY"
    / "SOL LONG MẠCH - HẬU THIÊN TĨNH"
    / "OS_WORK"
    / ".sandbox-bin"
    / "sol_archive_10_formats.py"
)
SPEC = importlib.util.spec_from_file_location("sol_archive_10_formats", SOURCE)
ARCHIVE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ARCHIVE)

SIGNATURES = {
    "7Z": (".7z", b"7z\xbc\xaf'\x1c"),
    "RAR": (".rar", b"Rar!\x1a\x07\x00"),
    "LR": (".lrz", b"LRZI"),
}


class OptionalAdapterTests(unittest.TestCase):
    def make_fixture(self, root, kind):
        suffix, signature = SIGNATURES[kind]
        path = root / ("sample" + suffix)
        path.write_bytes(signature + b"fixture-only-not-a-real-archive")
        return path

    def test_missing_optional_binaries_are_reported_as_needs_adapter(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(ARCHIVE.shutil, "which", return_value=None):
                for kind in SIGNATURES:
                    with self.subTest(kind=kind):
                        path = self.make_fixture(root, kind)
                        result = ARCHIVE.inspect(path)
                        self.assertEqual(result["detected"], kind)
                        self.assertEqual(result["status"], "NEEDS_ADAPTER")
                        self.assertIsNone(result["adapter"])
                        self.assertFalse(result["extraction_performed"])

    def test_adapter_dispatch_is_read_only_and_receipted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

            def which(name):
                if name in ("7z", "lrzip"):
                    return "/mock-bin/" + name
                return None

            with patch.object(ARCHIVE.shutil, "which", side_effect=which), patch.object(
                ARCHIVE.subprocess,
                "run",
                return_value=SimpleNamespace(returncode=0),
            ) as run:
                for kind in SIGNATURES:
                    with self.subTest(kind=kind):
                        path = self.make_fixture(root, kind)
                        before = ARCHIVE.sha(path)
                        result = ARCHIVE.inspect(path)
                        self.assertEqual(result["status"], "PASS")
                        self.assertEqual(result["sha256"], before)
                        self.assertTrue(result["adapter"])
                        self.assertFalse(result["extraction_performed"])
                self.assertEqual(run.call_count, len(SIGNATURES))

    def test_nonzero_adapter_exit_does_not_report_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make_fixture(Path(temp), "7Z")
            with patch.object(ARCHIVE.shutil, "which", side_effect=lambda n: "/mock-bin/7z" if n == "7z" else None), patch.object(
                ARCHIVE.subprocess,
                "run",
                return_value=SimpleNamespace(returncode=2),
            ):
                result = ARCHIVE.inspect(path)
            self.assertEqual(result["status"], "TEST_FAILED_OR_ENCRYPTED")
            self.assertFalse(result["extraction_performed"])

    def test_unsafe_member_paths_are_rejected(self):
        self.assertFalse(ARCHIVE.safe_member("../escape.txt"))
        self.assertFalse(ARCHIVE.safe_member(r"C:\escape.txt"))
        self.assertFalse(ARCHIVE.safe_member("link", symlink=True))
        self.assertTrue(ARCHIVE.safe_member("folder/data.txt"))


if __name__ == "__main__":
    unittest.main()
