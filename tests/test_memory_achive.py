"""Tests of SOURCE_DIRECT MEMORY_ACHIVE adapter without touching Computer or archive originals."""
import importlib.util
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "CHATGPT_LIBRARY" / "SOL LONG MẠCH - HẬU THIÊN TĨNH"
          / "OS_WORK" / ".sandbox-bin" / "memory_achive.py")
spec = importlib.util.spec_from_file_location("memory_achive", SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ArchiveTests(unittest.TestCase):
    def test_formats_exactly_ten(self):
        self.assertEqual(len(mod.FORMATS), 10)
        self.assertEqual(set(mod.FORMATS),
                         {"ALL", "7Z", "BZ2", "GZ", "JAR", "LR", "RAR", "TAR", "XZ", "ZIP"})
        self.assertIn("MEMORY_ARCHIVE_THỊT", str(mod.SOUL))
        self.assertEqual(mod.main(["formats"]), 0)

    def test_roundtrip_native_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "source.txt"
            data.write_text("thịt–ký ức\n" * 11, encoding="utf-8")
            for fmt, ext in [("ZIP",".zip"), ("JAR",".jar"), ("TAR",".tar"),
                             ("BZ2",".bz2"), ("GZ",".gz"), ("XZ",".xz")]:
                archive = root / ("test-" + fmt + ext)
                receipt = mod.pack([data], fmt, archive)
                self.assertEqual(receipt["status"], "PASS")
                self.assertEqual(mod.detect(archive), fmt)
                destination = root / ("restore-" + fmt)
                result = mod.unpack(archive, destination)
                self.assertEqual(result["status"], "PASS")
                self.assertEqual((destination / ("source.txt" if fmt in {"ZIP", "JAR", "TAR"} else archive.stem)).read_bytes(), data.read_bytes())
                with self.assertRaisesRegex(mod.ArchiveError, "DESTINATION_EXISTS"):
                    mod.unpack(archive, destination)
            self.assertEqual(len(mod.inventory(root)["items"]), 6)

    def test_block_zip_traversal_before_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "unsafe.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("../escape.txt", "no")
            with self.assertRaisesRegex(mod.ArchiveError, "UNSAFE_MEMBER_PATH"):
                mod.unpack(archive, root / "out")
            self.assertFalse((root / "out").exists())
            self.assertFalse((root / "escape.txt").exists())

    def test_block_tar_symlink_before_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "unsafe.tar"
            with tarfile.open(archive, "w") as t:
                link = tarfile.TarInfo("link")
                link.type = tarfile.SYMTYPE
                link.linkname = "../../escape"
                t.addfile(link)
            with self.assertRaisesRegex(mod.ArchiveError, "UNSAFE_ARCHIVE_TYPE"):
                mod.unpack(archive, root / "out")
            self.assertFalse((root / "out").exists())

    def test_unknown_does_not_create_anything(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data.bin"
            data.write_bytes(b"not an archive")
            with self.assertRaisesRegex(mod.ArchiveError, "UNKNOWN_FORMAT"):
                mod.unpack(data, root / "restored")
            self.assertFalse((root / "restored").exists())

    def test_cli_read_only_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "plain.txt").write_text("keep source", encoding="utf-8")
            before = {p.name for p in root.iterdir()}
            p = subprocess.run([sys.executable, str(SOURCE), "inventory", str(root)],
                               capture_output=True, text=True, check=False)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(json.loads(p.stdout)["count"], 0)
            self.assertEqual(before, {p.name for p in root.iterdir()})


if __name__ == "__main__":
    unittest.main()
