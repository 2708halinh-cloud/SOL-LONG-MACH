import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from tool_forge import scan, plugin_scaffold

class TestForge(unittest.TestCase):
    def test_audit_no_auto_delete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'SKILL.md').write_text('Chỉ được do x; forbidden by y\nsecret=SHOULD_NOT_APPEAR', encoding='utf-8')
            result=scan(root)
            self.assertTrue(result['never_autouninstall'])
            self.assertEqual(result['files'][0]['status'], 'REVIEW_REQUIRED')
            self.assertNotIn('SHOULD_NOT_APPEAR', json.dumps(result))
    def test_forge_never_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            src=root/'plugin.json'
            src.write_text(json.dumps({'name':'source-plugin'}), encoding='utf-8')
            out=root/'new-plugin'
            plugin_scaffold(src, out, 'new-plugin')
            self.assertFalse(json.loads((out/'SOURCE.json').read_text())['functionality_implemented'])
            with self.assertRaises(FileExistsError):
                plugin_scaffold(src, out, 'new-plugin')
    def test_invalid_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'plugin.json'
            src.write_text('{}')
            with self.assertRaises(ValueError):
                plugin_scaffold(src, root/'new', '../../bad')

if __name__=='__main__':
    unittest.main()
