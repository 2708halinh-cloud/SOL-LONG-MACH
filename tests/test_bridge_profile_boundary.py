import unittest
import os
import types
from unittest import mock

class ProfileSourceBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        namespace = {"__file__": "/tmp/bridge.py", "__name__": "boundary_profile_only"}
        exec(compile(__import__("pathlib").Path(__file__).resolve().parents[1].joinpath("LOCAL_BRIDGE", "bridge.py").read_text(encoding="utf-8").split("ROOT = Path(__file__).resolve().parents[1]")[0], "bridge.py", "exec"), namespace)
        cls.ns = namespace

    def setUp(self):
        self.ns["windows_user_profile"].cache_clear()
        self.ns["wsl_user_profile"].cache_clear()

    def test_local_name_is_dynamic_not_source(self):
        with mock.patch.dict(os.environ, {
            "SOL_WINDOWS_USERPROFILE": r"C:\Users\OtherName",
            "SOL_WSL_USERPROFILE": "/mnt/c/Users/OtherName"
        }):
            self.assertEqual(self.ns["win_profile"]("AppData", "Local", "Temp", "bridge.ps1"),
                             r"C:\Users\OtherName\AppData\Local\Temp\bridge.ps1")
            self.assertEqual(str(self.ns["wsl_profile"]("AppData", "Local")),
                             "/mnt/c/Users/OtherName/AppData/Local")

    def test_windows_resolve_uses_real_host_profile(self):
        with mock.patch.dict(os.environ, {"SOL_WINDOWS_USERPROFILE": "", "USERPROFILE": ""}):
            with mock.patch.object(self.ns["subprocess"], "run") as run:
                run.return_value = types.SimpleNamespace(returncode=0, stdout="C:\\Users\\DifferentName\n")
                self.assertEqual(str(self.ns["windows_user_profile"]()), "C:\\Users\\DifferentName")
                self.assertEqual(run.call_args.args[0][0], "powershell.exe")

    def test_invalid_windows_path_rejected(self):
        with mock.patch.dict(os.environ, {"SOL_WINDOWS_USERPROFILE": "relative-folder"}):
            with self.assertRaises(RuntimeError):
                self.ns["windows_user_profile"]()

    def test_wsl_path_derived_not_embedded(self):
        with mock.patch.dict(os.environ, {
            "SOL_WINDOWS_USERPROFILE": r"C:\Users\ThirdName",
            "SOL_WSL_USERPROFILE": "",
        }):
            with mock.patch.object(self.ns["subprocess"], "run") as run:
                run.return_value = types.SimpleNamespace(returncode=0, stdout="/mnt/c/Users/ThirdName\n")
                self.assertEqual(str(self.ns["wsl_user_profile"]()), "/mnt/c/Users/ThirdName")
                self.assertEqual(run.call_args.args[0][0], "wslpath")

    def test_specific_user_profile_not_hardcoded_in_production(self):
        self.assertNotIn("C:\\Users\\halin", __import__("pathlib").Path(__file__).resolve().parents[1].joinpath("LOCAL_BRIDGE", "bridge.py").read_text(encoding="utf-8"))
        self.assertNotIn("/mnt/c/Users/halin", FULL_BRIDGE)

if __name__ == "__main__":
    unittest.main()
