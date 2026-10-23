"""Verify that HelloHabit T005 carrier is NOT represented as app installation."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from runtime.hellohabit_t005_adapter import BINDING,inspect

ROOT=Path(__file__).resolve().parents[1]

class HelloHabitT005Tests(unittest.TestCase):
    def test_known_manifest_identity(self):
        receipt=inspect(ROOT)
        self.assertEqual(receipt["package"],"com.studio.hellohabit")
        self.assertEqual(receipt["split"],"config.xxhdpi")
        self.assertEqual(receipt["version_code"],572)
        self.assertTrue(receipt["T005_package_identity_registered"])

    def test_split_is_not_app_installation(self):
        receipt=inspect(ROOT)
        self.assertFalse(receipt["has_code"])
        self.assertFalse(receipt["installed_on_android_proven"])
        self.assertFalse(receipt["real_habit_data_sync_proven"])
        self.assertFalse(receipt["provider_permissions_bypassed"])

    def test_fabricated_install_claim_is_rejected(self):
        data=json.loads((ROOT/BINDING).read_text())
        data["android_apk_installed"]=True
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/BINDING
            p.parent.mkdir(parents=True)
            p.write_text(json.dumps(data),encoding="utf-8")
            with self.assertRaises(AssertionError):
                inspect(Path(td))

    def test_changed_package_is_rejected(self):
        data=json.loads((ROOT/BINDING).read_text())
        data["user_supplied_manifest"]["manifest"]["package"]="other.package"
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/BINDING
            p.parent.mkdir(parents=True)
            p.write_text(json.dumps(data),encoding="utf-8")
            with self.assertRaisesRegex(AssertionError,"PACKAGE_MISMATCH"):
                inspect(Path(td))

if __name__=="__main__": unittest.main()
