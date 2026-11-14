"""Offline, side-effect-free tests for Google Cloud usage guard."""
import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "gcp_usage_guard.py"
spec = importlib.util.spec_from_file_location("gcp_usage_guard", MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class GuardTests(unittest.TestCase):
    def test_reported_metrics(self):
        data = module.analyse([
            {"Tên": "API Compute Engine", "Yêu cầu": "49", "Lỗi (%)": "100",
             "Độ trễ trung bình (ms)": "36", "Độ trễ ở phân vị thứ 95 (ms)": "77"},
            {"Tên": "API App Hub", "Yêu cầu": 15, "Lỗi (%)": 0},
            {"Tên": "API lưu trữ đám mây", "Yêu cầu": 4, "Lỗi (%)": 100},
            {"Tên": "API AlloyDB", "Yêu cầu": "—", "Lỗi (%)": "—"},
        ])
        self.assertEqual(data["known_requests"], 68)
        self.assertEqual(data["estimated_failed_requests"], 53)
        self.assertEqual(data["provider_api_calls"], 0)
        self.assertEqual(data["items"][0]["action"], "STOP_AUTOMATIC_RETRY_INVESTIGATE_ERRORS")
        self.assertEqual(data["items"][3]["action"], "NO_DATA_DO_NOT_INFER_ZERO")
        self.assertTrue(data["cost"].startswith("UNKNOWN"))

    def test_invalid_percentage_rejected(self):
        with self.assertRaises(ValueError):
            module.analyse([{"api": "foo", "requests": 1, "error_percent": 101}])


if __name__ == "__main__":
    unittest.main()
