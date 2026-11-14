import json
from pathlib import Path
import sys
import unittest

ROOT=next(x for x in Path(__file__).resolve().parents if x.name=="SOL LONG MẠCH - HẬU THIÊN TĨNH") / "COMPUTER_KHÍ💜BRAIN_OS_POWER"
TOOLS=Path(__file__).resolve().parent
sys.path.insert(0,str(TOOLS))
from registry_hive_router import validate,resolve


class FiveHivesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads((ROOT/'CORE_PLACES_INDEX_MÁU_🔴_HỎA_REALITY'/'WINDOWS_REGISTRY_EDITOR_HIVES_CURRENT.json').read_text())
    def test_five_hives_unique(self):
        validate(self.doc)
    def test_computer_is_virtual_root(self):
        self.assertEqual(resolve(self.doc,'Computer')['stone'],'POWER')
        self.assertFalse(resolve(self.doc,'Computer')['windows_is_hive'])
    def test_five_stone_files_exist(self):
        for item in self.doc['five_hives']:
            file=ROOT/item['folder']/'REGISTRY_HIVE_BINDING_CURRENT.json'
            self.assertTrue(file.is_file(),str(file))
            bind=json.loads(file.read_text())
            self.assertEqual(bind['hive'],item['hive'])
            self.assertEqual(bind['stone'],item['stone'])
    def test_aliases_and_views(self):
        self.assertEqual(resolve(self.doc,'HKCU')['stone'],'MIND')
        self.assertEqual(resolve(self.doc,'HKCR')['stone'],'SPACE')
        self.assertEqual(resolve(self.doc,'HKLM')['stone'],'REALITY')
        self.assertEqual(resolve(self.doc,'HKU')['stone'],'SOUL')
        self.assertEqual(resolve(self.doc,'HKCC')['stone'],'TIME')
        self.assertIn('VIEW_OF',self.doc['relationships']['HKCU'])
    def test_no_registry_mutation(self):
        self.assertIn('NO_REGISTRY_WRITE',self.doc['real_windows_registry_write_state'])


if __name__=='__main__':
    unittest.main()
