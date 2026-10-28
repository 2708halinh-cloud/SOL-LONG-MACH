"""Real optional-backend integration tests.

These tests run only in the isolated archive-adapter branch after CI installs 7zip
and lrzip. They create temporary fixtures, never extract archive contents, and
never modify source carriers. RAR is explicitly fail-closed unless a real fixture
is supplied; a signature-only byte sequence is not treated as a valid archive.
"""
import hashlib
import importlib.util
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIN_DIR = (
    ROOT
    / "CHATGPT_LIBRARY"
    / "SOL LONG MẠCH - HẬU THIÊN TĨNH"
    / "OS_WORK"
    / ".sandbox-bin"
)
SOL_SOURCE = BIN_DIR / "sol_archive_10_formats.py"
MEMORY_SOURCE = BIN_DIR / "memory_achive.py"

RAR_FIXTURE_UPSTREAM_COMMIT = "7574249bdc19f34c63b52ef0102d056f4fb7ba39"
RAR_FIXTURE_UPSTREAM_BLOB_SHA1 = "f197a2983302f5829de2719bdddcf43b8c59b201"
RAR_FIXTURE_RAW_SHA256 = "d421b86f6290aefad61b2a36737253b2b30fe27c156bd95abfc230f24fe0307e"


def load_module(name, source):
    spec = importlib.util.spec_from_file_location(name, source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SOL_ARCHIVE = load_module("sol_archive_10_formats_real", SOL_SOURCE)
MEMORY_ARCHIVE = load_module("memory_achive_real", MEMORY_SOURCE)


class RealOptionalBackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sevenzip = shutil.which("7zz") or shutil.which("7z")
        cls.lrzip = shutil.which("lrzip")
        if not cls.sevenzip:
            raise AssertionError("CI_BACKEND_MISSING: install package providing 7zz/7z")
        if not cls.lrzip:
            raise AssertionError("CI_BACKEND_MISSING: install lrzip")

    def make_source(self, root):
        source = root / "source.txt"
        source.write_bytes(b"SOL read-only archive fixture\n" * 7)
        return source, source.read_bytes(), hashlib.sha256(source.read_bytes()).hexdigest()

    def make_7z(self, root, source):
        archive = root / "fixture.7z"
        proc = subprocess.run(
            [self.sevenzip, "a", "-t7z", archive.name, source.name],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        self.assertTrue(archive.is_file())
        return archive

    def make_lr(self, root, source):
        archive = root / "fixture.lrz"
        proc = subprocess.run(
            [self.lrzip, "-o", archive.name, source.name],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        self.assertTrue(archive.is_file(), proc.stdout + proc.stderr)
        return archive

    def test_real_7z_archive_is_integrity_checked_without_extraction(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, before, source_sha = self.make_source(root)
            archive = self.make_7z(root, source)
            archive_sha = hashlib.sha256(archive.read_bytes()).hexdigest()

            result = SOL_ARCHIVE.inspect(archive)
            self.assertEqual(result["detected"], "7Z")
            self.assertEqual(result["status"], "PASS", result)
            self.assertEqual(result["adapter"], Path(self.sevenzip).name)
            self.assertEqual(result["sha256"], archive_sha)
            self.assertFalse(result["extraction_performed"])
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), source_sha)
            self.assertEqual(source.read_bytes(), before)

            receipt = MEMORY_ARCHIVE.test_archive(archive)
            self.assertEqual(receipt["status"], "PASS", receipt)
            self.assertEqual(receipt["format"], "7Z")
            self.assertEqual(receipt["sha256"], archive_sha)

            destination = root / "must-not-be-created"
            with self.assertRaisesRegex(MEMORY_ARCHIVE.ArchiveError, "SAFE_EXTRACT_HANDLER_REQUIRED"):
                MEMORY_ARCHIVE.unpack(archive, destination)
            self.assertFalse(destination.exists())
            self.assertEqual(source.read_bytes(), before)

    def test_real_lr_archive_is_integrity_checked_without_extraction(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, before, source_sha = self.make_source(root)
            archive = self.make_lr(root, source)
            archive_sha = hashlib.sha256(archive.read_bytes()).hexdigest()

            result = SOL_ARCHIVE.inspect(archive)
            self.assertEqual(result["detected"], "LR")
            self.assertEqual(result["status"], "PASS", result)
            self.assertEqual(result["adapter"], Path(self.lrzip).name)
            self.assertEqual(result["sha256"], archive_sha)
            self.assertFalse(result["extraction_performed"])
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), source_sha)
            self.assertEqual(source.read_bytes(), before)

            receipt = MEMORY_ARCHIVE.test_archive(archive)
            self.assertEqual(receipt["status"], "PASS", receipt)
            self.assertEqual(receipt["format"], "LR")
            self.assertEqual(receipt["sha256"], archive_sha)

    def test_malformed_7z_fails_closed_and_does_not_extract(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            bad = root / "malformed.7z"
            bad.write_bytes(b"7z\xbc\xaf'\x1c" + b"not-a-real-archive")
            before = bad.read_bytes()

            result = SOL_ARCHIVE.inspect(bad)
            self.assertEqual(result["detected"], "7Z")
            self.assertNotEqual(result["status"], "PASS", result)
            self.assertFalse(result["extraction_performed"])
            self.assertEqual(bad.read_bytes(), before)
            self.assertFalse((root / "extract").exists())

    def test_signature_only_rar_is_never_claimed_as_verified(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fake = root / "signature-only.rar"
            fake.write_bytes(b"Rar!\x1a\x07\x00" + b"not-a-real-rar")
            before = fake.read_bytes()

            result = SOL_ARCHIVE.inspect(fake)
            self.assertEqual(result["detected"], "RAR")
            self.assertNotEqual(result["status"], "PASS", result)
            self.assertFalse(result["extraction_performed"])
            self.assertEqual(fake.read_bytes(), before)

            with self.assertRaises(MEMORY_ARCHIVE.ArchiveError):
                MEMORY_ARCHIVE.test_archive(fake)


    def test_real_rar_fixture_is_integrity_checked_without_extraction(self):
        # Pinned source: libarchive/libarchive@7574249bdc19f34c63b52ef0102d056f4fb7ba39
        # Path: libarchive/test/test_read_format_rar.rar.uu
        # The workflow verifies upstream Git blob SHA-1 before decoding the 336-byte RAR.
        fixture_path = os.environ.get("SOL_RAR_FIXTURE_PATH")
        self.assertTrue(fixture_path, "CI_RAR_FIXTURE_NOT_PROVISIONED")
        archive = Path(fixture_path)
        self.assertTrue(archive.is_file(), "CI_RAR_FIXTURE_MISSING")
        original_bytes = archive.read_bytes()
        archive_sha = hashlib.sha256(original_bytes).hexdigest()
        self.assertEqual(archive_sha, RAR_FIXTURE_RAW_SHA256)

        result = SOL_ARCHIVE.inspect(archive)
        self.assertEqual(result["detected"], "RAR")
        self.assertEqual(result["status"], "PASS", result)
        self.assertEqual(result["adapter"], Path(self.sevenzip).name)
        self.assertEqual(result["sha256"], archive_sha)
        self.assertFalse(result["extraction_performed"])

        receipt = MEMORY_ARCHIVE.test_archive(archive)
        self.assertEqual(receipt["status"], "PASS", receipt)
        self.assertEqual(receipt["format"], "RAR")
        self.assertEqual(receipt["sha256"], archive_sha)

        destination = archive.parent / "must-not-be-created-rar"
        with self.assertRaisesRegex(MEMORY_ARCHIVE.ArchiveError, "SAFE_EXTRACT_HANDLER_REQUIRED"):
            MEMORY_ARCHIVE.unpack(archive, destination)
        self.assertFalse(destination.exists())
        self.assertEqual(archive.read_bytes(), original_bytes)

if __name__ == "__main__":
    unittest.main()
