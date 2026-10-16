"""Guard the observed T007/OPEN source against agent-authored terminal-label regressions."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools'
SOURCE = ROOT / 'CONFIG_SOL/OPEN_AND_CONFLICT_CURRENT.md'
SIX = ROOT / 'CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/MEMORY_ARCHIVE_THỊT🟠THỔ_SOUL/00_OPEN_0D_CONTINUITY/02_QUAN_HE_OPEN_6_MAT.md'

class T007IngressRegression(unittest.TestCase):
    def test_original_ingress_source_unchanged_in_meaning(self):
        original = SOURCE.read_text(encoding='utf-8')
        self.assertIn('OPEN = TIẾP NHẬN TÍN HIỆU TRỰC TIẾP.', original)
        self.assertIn('OPEN không phải pending, waiting, unfinished hay unverified.', original)
        self.assertIn('Xác định FIRST_AFFECTED_CAUSE.', original)

    def test_six_faces_not_collapsed_into_status(self):
        original = SIX.read_text(encoding='utf-8')
        for face in ('MAP / TRUY TÌM', 'INPUT / DUYÊN KHỞI', 'CÔNG CỤ', 'THỜI GIAN THỰC', 'SỬA LỖI TRẠNG THÁI', 'TRƯỜNG / NEURON'):
            self.assertIn(face, original)

    def test_router_has_no_old_silent_output_gate(self):
        current = (TOOL/'POWER_ROUTER.md').read_text(encoding='utf-8')
        self.assertIn('OPEN = TIẾP NHẬN TÍN HIỆU TRỰC TIẾP', current)
        self.assertIn('FIRST_AFFECTED_CAUSE', current)
        self.assertNotIn('Cổng `READBACK` của `Toolset.md` chỉ phát', current)
        self.assertNotIn('Theo cổng `READBACK = NEXT CỦA TÔI`', current)

    def test_correction_belongs_to_toolchain_and_retains_consequence_boundary(self):
        p = TOOL/'Chuỗi công cụ/_Sổ_đăng_ký/T007_OPEN_INGRESS_CORRECTION_20261016.md'
        record = p.read_text(encoding='utf-8')
        self.assertIn('agent-origin misrouting', record)
        self.assertIn('not a status label', record)
        self.assertIn('Document correction does not undo the past', record)

if __name__ == '__main__':
    unittest.main()
