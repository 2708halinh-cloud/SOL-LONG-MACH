import unittest
from unittest.mock import Mock
from xiaomi_notes_tool import dispatch

class TestXiaomiNotesTool(unittest.TestCase):
    def test_valid_dispatch_targets_actual_notes(self):
        runner = Mock(return_value=Mock(returncode=0))
        result = dispatch('Neutron (0) = TÂM', runner=runner)
        command = runner.call_args.args[0]
        self.assertEqual(command[0], 'am')
        self.assertEqual(command[command.index('-p')+1], 'com.miui.notes')
        self.assertEqual(command[command.index('--es')+2], 'Neutron (0) = TÂM')
        self.assertTrue(result['intent_accepted'])
        self.assertFalse(result['saved_note_verified'])
    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            dispatch('   ')
    def test_launch_error_classified(self):
        res = dispatch('test',runner=Mock(return_value=Mock(returncode=1)))
        self.assertFalse(res['intent_accepted'])
        self.assertEqual(res['result_class'], 'INTENT_FAILED')

if __name__ == '__main__':
    unittest.main()
