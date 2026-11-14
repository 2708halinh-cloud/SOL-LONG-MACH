import json, tempfile, unittest
from pathlib import Path
from roots_windows import PALETTE, DRIVE_ROOT_CONSTANTS, build_registry, drive_slot, save, check_canonical_mirror

class MappingTests(unittest.TestCase):
    def test_c(self):
        self.assertEqual(drive_slot('C:'),'ROOTS_LEVER_0.1')
    def test_d(self):
        self.assertEqual(drive_slot('D:\\'),'ROOTS_LEVER_0.2')
    def test_w_stability(self):
        self.assertEqual(drive_slot('W'),'ROOTS_LEVER_0.21')
    def test_letter_invalid(self):
        with self.assertRaises(ValueError):drive_slot('../D')
    def test_reserved_outside_root_map(self):
        with self.assertRaises(ValueError):drive_slot('A:')
    def test_fixed_mapping_is_constant_not_inferred_from_mounts(self):
        self.assertEqual(len(DRIVE_ROOT_CONSTANTS),24)
        self.assertEqual(DRIVE_ROOT_CONSTANTS['C'], 'ROOTS_LEVER_0.1')
        self.assertEqual(DRIVE_ROOT_CONSTANTS['D'], 'ROOTS_LEVER_0.2')
        self.assertEqual(DRIVE_ROOT_CONSTANTS['W'], 'ROOTS_LEVER_0.21')
        self.assertEqual(DRIVE_ROOT_CONSTANTS['Z'], 'ROOTS_LEVER_0.24')
    def test_d_violet(self):
        data=build_registry([{'letter':'D','root':'D:\\'}],[{'letter':'D','filesystem':'NTFS','guid':r'\\?\Volume{ab}\\'}])
        self.assertEqual(data['carriers'][0]['hair_tone']['symbol'],'🟣')
        self.assertEqual(data['carriers'][0]['provider'],'WINDOWS_VOLUME')
    def test_no_unknown_palettes(self):
        data=build_registry([{'letter':'I','root':'I:\\','is_google_drive':True}],[])
        self.assertNotIn('hair_tone',data['carriers'][0])
        self.assertEqual(data['carriers'][0]['bridge'],'GOOGLE_DRIVE_MOUNT')
    def test_stable_independent_of_mount_count(self):
        a=build_registry([{'letter':'D'}],[])
        b=build_registry([{'letter':'C'},{'letter':'D'},{'letter':'W'}],[])
        self.assertEqual(a['carriers'][0]['roots_id'],b['carriers'][1]['roots_id'])
    def test_canonical_mirror_conflict_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'constant.json'
            path.write_text(json.dumps({'namespace':'ROOTS_WINDOWS_DRIVE_LETTERS','mapping':{'C:\\':'ROOTS_LEVER_0.2'}}))
            with self.assertRaises(RuntimeError):check_canonical_mirror(path)
    def test_atomic_unchanged_no_rewrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'roots.json'
            data=build_registry([{'letter':'C'}],[])
            self.assertTrue(save(data,path))
            self.assertFalse(save(data,path))
            self.assertEqual(json.loads(path.read_text(encoding='utf-8'))['carrier_count'],1)
    def test_six_palette_keys(self):
        self.assertEqual(sorted(PALETTE),[1,2,3,4,5,6])
    def test_no_duplicate_on_scan(self):
        obj=build_registry([{'letter':'D'},{'letter':'D'}],[])
        self.assertEqual(len(obj['carriers']),1)

if __name__=='__main__': unittest.main()