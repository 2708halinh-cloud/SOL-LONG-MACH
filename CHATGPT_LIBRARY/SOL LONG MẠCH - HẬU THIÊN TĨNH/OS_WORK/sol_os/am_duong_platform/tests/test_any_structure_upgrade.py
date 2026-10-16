import unittest,sys
from pathlib import Path
HERE=Path(__file__).resolve()
MODULE_DIR=HERE.parent.parent if (HERE.parent.name=="tests" and (HERE.parent.parent/"any_structure.py").is_file()) else HERE.parent
if not (MODULE_DIR/"any_structure.py").is_file():
    MODULE_DIR=HERE.parents[1]/"CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/sol_os/am_duong_platform"
sys.path.insert(0,str(MODULE_DIR))
from any_structure import units,inspect_multilingual,translate_structure,translate_any
class LanguageTests(unittest.TestCase):
    def test_source_lossless(self):
        for s in ["", "xin chào\r\n  rất tốt \n", "你好 世界 مرحبا 안녕 😊", "đi đi, đọc sách"]:
            got=inspect_multilingual(s,language_hint="vi")
            self.assertEqual(got['source'],s)
            self.assertEqual(''.join(x['prefix']+x['raw']+x['suffix']+x['newline'] for x in got['lines']),s)
    def test_pos_not_verified(self):
        g=inspect_multilingual('mẹ đọc sách',language_hint='vi')
        self.assertTrue(any('noun' in t['pos_candidates'] for t in g['tokens']))
        self.assertTrue(all(not t['pos_verified'] for t in g['tokens']))
    def test_repetition(self):
        g=inspect_multilingual('đi đi chạy-chạy',language_hint='vi')
        self.assertTrue(g['repetitions'])
    def test_nested(self):
        data={'person':{'name':' Hà Linh\n','roles':['dịch dữ liệu','  ']},'ok':True,'count':3,'none':None}
        out=translate_structure(data,'en',approved=True,translate_part=lambda t,target,source:'['+t+']')
        self.assertEqual(out['translation']['person']['roles'][0],'[dịch dữ liệu]')
        self.assertEqual(out['translation']['person']['name'],' [Hà Linh]\n')
        self.assertEqual(out['translation']['ok'],True)
        self.assertEqual(out['translation']['none'],None)
        self.assertEqual(out['source'],data)
        self.assertEqual(len(out['paths_translated']),2)
    def test_no_consent(self):
        with self.assertRaises(ValueError):
            translate_structure({'a':'bonjour'},'en',translate_part=lambda t,target,source:t)
    def test_limits(self):
        with self.assertRaises(ValueError):
            translate_structure({'a':['x']*600},'en',approved=True,translate_part=lambda t,target,source:t)
    def test_no_unsupported_type(self):
        with self.assertRaises(ValueError):
            translate_structure({'x':{1,2}},'en',approved=True,translate_part=lambda t,target,source:t)
if __name__=='__main__':unittest.main()