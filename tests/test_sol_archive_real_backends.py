"""Real optional-backend integration tests.

These tests run only in the isolated archive-adapter branch after CI installs 7zip
and lrzip. They create temporary fixtures, never extract archive contents, and
never modify source carriers. RAR is explicitly fail-closed unless a real fixture
is supplied; a signature-only byte sequence is not treated as a valid archive.
"""
import hashlib
import json
import importlib.util
import os
import shutil
import subprocess
import tempfile
import sys
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

    def test_nine_format_capability_and_source_target_hash_matrix(self):
        expected_all = ["ALL", "7Z", "BZ2", "GZ", "JAR", "LR", "RAR", "TAR", "XZ", "ZIP"]
        expected_concrete = ["7Z", "BZ2", "GZ", "JAR", "LR", "RAR", "TAR", "XZ", "ZIP"]
        caps_proc = subprocess.run(
            [sys.executable, str(SOL_SOURCE), "--capabilities"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(caps_proc.returncode, 0, caps_proc.stderr)
        capabilities = json.loads(caps_proc.stdout)
        self.assertEqual(capabilities["formats"], expected_all)
        for optional in ("7Z", "RAR", "LR"):
            self.assertTrue(capabilities[optional], capabilities)

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, original_source_bytes, source_sha = self.make_source(root)
            matrix = {}
            native_extensions = {
                "ZIP": ".zip", "JAR": ".jar", "TAR": ".tar",
                "BZ2": ".bz2", "GZ": ".gz", "XZ": ".xz",
            }

            for kind, extension in native_extensions.items():
                archive = root / ("matrix-" + kind + extension)
                pack_receipt = MEMORY_ARCHIVE.pack([source], kind, archive)
                self.assertEqual(pack_receipt["status"], "PASS", pack_receipt)
                archive_before = hashlib.sha256(archive.read_bytes()).hexdigest()
                test_receipt = MEMORY_ARCHIVE.test_archive(archive)
                self.assertEqual(test_receipt["status"], "PASS", test_receipt)

                destination = root / ("restore-" + kind)
                unpack_receipt = MEMORY_ARCHIVE.unpack(archive, destination)
                self.assertEqual(unpack_receipt["status"], "PASS", unpack_receipt)
                restored = destination / (
                    "source.txt" if kind in {"ZIP", "JAR", "TAR"} else archive.stem
                )
                restored_sha = hashlib.sha256(restored.read_bytes()).hexdigest()
                archive_after = hashlib.sha256(archive.read_bytes()).hexdigest()
                self.assertEqual(restored_sha, source_sha)
                self.assertEqual(archive_after, archive_before)
                self.assertEqual(source.read_bytes(), original_source_bytes)

                matrix[kind] = {
                    "backend": "python-native",
                    "status": "PASS",
                    "source_file_sha256": source_sha,
                    "target_archive_sha256_before": archive_before,
                    "target_archive_sha256_after": archive_after,
                    "archive_hash_stable": archive_after == archive_before,
                    "roundtrip_target_sha256": restored_sha,
                    "source_target_hash_match": restored_sha == source_sha,
                    "source_unchanged": source.read_bytes() == original_source_bytes,
                    "extraction_performed": True,
                }

            for kind, archive in (("7Z", self.make_7z(root, source)), ("LR", self.make_lr(root, source))):
                archive_before = hashlib.sha256(archive.read_bytes()).hexdigest()
                result = SOL_ARCHIVE.inspect(archive)
                self.assertEqual(result["status"], "PASS", result)
                self.assertEqual(result["detected"], kind)
                receipt = MEMORY_ARCHIVE.test_archive(archive)
                self.assertEqual(receipt["status"], "PASS", receipt)
                archive_after = hashlib.sha256(archive.read_bytes()).hexdigest()
                self.assertEqual(archive_after, archive_before)
                self.assertEqual(source.read_bytes(), original_source_bytes)
                self.assertFalse(result["extraction_performed"])

                matrix[kind] = {
                    "backend": result["adapter"],
                    "status": "PASS",
                    "source_file_sha256": source_sha,
                    "target_archive_sha256_before": archive_before,
                    "target_archive_sha256_after": archive_after,
                    "archive_hash_stable": archive_after == archive_before,
                    "roundtrip_target_sha256": None,
                    "source_target_hash_match": None,
                    "source_unchanged": source.read_bytes() == original_source_bytes,
                    "extraction_performed": False,
                }

            rar_fixture_path = os.environ.get("SOL_RAR_FIXTURE_PATH")
            self.assertTrue(rar_fixture_path, "CI_RAR_FIXTURE_NOT_PROVISIONED")
            rar_archive = Path(rar_fixture_path)
            rar_before_bytes = rar_archive.read_bytes()
            rar_before = hashlib.sha256(rar_before_bytes).hexdigest()
            self.assertEqual(rar_before, RAR_FIXTURE_RAW_SHA256)
            rar_result = SOL_ARCHIVE.inspect(rar_archive)
            self.assertEqual(rar_result["detected"], "RAR")
            self.assertEqual(rar_result["status"], "PASS", rar_result)
            rar_receipt = MEMORY_ARCHIVE.test_archive(rar_archive)
            self.assertEqual(rar_receipt["status"], "PASS", rar_receipt)
            rar_after_bytes = rar_archive.read_bytes()
            rar_after = hashlib.sha256(rar_after_bytes).hexdigest()
            self.assertEqual(rar_after, rar_before)
            self.assertEqual(rar_after_bytes, rar_before_bytes)
            self.assertFalse(rar_result["extraction_performed"])

            matrix["RAR"] = {
                "backend": rar_result["adapter"],
                "status": "PASS",
                "source_file_sha256": None,
                "target_archive_sha256_before": rar_before,
                "target_archive_sha256_after": rar_after,
                "archive_hash_stable": rar_after == rar_before,
                "roundtrip_target_sha256": None,
                "source_target_hash_match": None,
                "source_unchanged": True,
                "extraction_performed": False,
                "fixture_source_commit": RAR_FIXTURE_UPSTREAM_COMMIT,
                "fixture_source_git_blob_sha1": RAR_FIXTURE_UPSTREAM_BLOB_SHA1,
                "fixture_sha256": RAR_FIXTURE_RAW_SHA256,
            }

            self.assertEqual(set(matrix), set(expected_concrete))
            self.assertTrue(all(item["status"] == "PASS" for item in matrix.values()))
            self.assertTrue(all(item["archive_hash_stable"] for item in matrix.values()))
            self.assertTrue(all(item["source_unchanged"] for item in matrix.values()))
            self.assertTrue(all(item["source_target_hash_match"] for item in matrix.values() if item["source_target_hash_match"] is not None))
            self.assertFalse(SOL_ARCHIVE.safe_member("../escape.txt"))
            with self.assertRaisesRegex(MEMORY_ARCHIVE.ArchiveError, "UNSAFE_MEMBER_PATH"):
                MEMORY_ARCHIVE.validate_member("../escape.txt")
            self.assertFalse((root / "escape.txt").exists())
            self.assertEqual(source.read_bytes(), original_source_bytes)

            receipt = {
                "schema": "SOL_ARCHIVE_CAPABILITY_HASH_MATRIX_V1",
                "format_count": len(matrix),
                "capability_formats_including_virtual_all": capabilities["formats"],
                "formats": matrix,
                "source_file_sha256": source_sha,
                "source_file_unchanged": source.read_bytes() == original_source_bytes,
                "all_archive_hashes_stable": all(item["archive_hash_stable"] for item in matrix.values()),
                "all_native_roundtrip_hashes_match": all(
                    item["source_target_hash_match"] is True
                    for item in matrix.values()
                    if item["source_target_hash_match"] is not None
                ),
                "path_traversal_rejected": True,
                "malformed_7z_fails_closed": True,
                "extraction_policy": "NO_EXTRACTION_FOR_7Z_RAR_LR;NATIVE_FORMAT_ROUNDTRIPS_USE_TEMPORARY_FIXTURES_ONLY",
            }
            output = os.environ.get("SOL_ARCHIVE_MATRIX_OUTPUT")
            target = Path(output) if output else root / "sol-archive-capability-hash-matrix.json"
            self.assertFalse(target.exists(), "Refuse to overwrite existing matrix receipt")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            readback = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(readback, receipt)
            print("SOL_ARCHIVE_MATRIX_RECEIPT=" + json.dumps(receipt, ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    unittest.main()
