import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = (Path(__file__).resolve().parents[1]
          / 'CHATGPT_LIBRARY' / 'SOL LONG MẠCH - HẬU THIÊN TĨNH'
          / 'OS_WORK' / 'brainwave_logger.py')
spec = importlib.util.spec_from_file_location('brainwave_logger', MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class FakeLogprobs:
    def model_dump(self, mode='json'):
        return {'content': [{'token': 'OK', 'logprob': -0.1, 'top_logprobs': []}]}

class FakeChoice:
    def __init__(self, logprobs=None):
        self.message = type('Message', (), {'content': 'Trả lời không chứa mã bí mật'})()
        self.logprobs = logprobs
        self.finish_reason = 'stop'

class FakeResponse:
    def __init__(self, logprobs=None):
        self.model = 'mock-test-no-api'
        self.choices = [FakeChoice(logprobs)]
        self.usage = {'total_tokens': 3}

class FakeClient:
    def __init__(self, response, error=None):
        self.response = response
        self.error = error
        self.calls = []
        self.chat = type('Chat', (), {})()
        self.chat.completions = type('Completions', (), {})()
        self.chat.completions.create = self.create
    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error: raise self.error
        return self.response

def events(directory, key):
    return [json.loads(x) for x in (directory / module.LAYERS[key]).read_text(encoding='utf-8').splitlines() if x.strip()]

class LoggerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.logger = module.Journal(self.home)
    def test_create_exactly_five_journals(self):
        self.assertEqual(sorted(x.name for x in self.home.iterdir()), sorted(module.LAYERS.values()))
        self.assertEqual(events(self.home, 'raw'), [])
    def test_no_api_demo_does_not_make_up_logprobs(self):
        self.assertIsNone(module.execute_neural_turn('INPUT: Đông Bắc', journal=self.logger, dry_run=True))
        self.assertEqual(events(self.home, 'spatial')[0]['data']['input_view']['direction_code'], 'NE')
        self.assertFalse(events(self.home, 'chrono')[-1]['data']['provider_called'])
        self.assertFalse(events(self.home, 'logprobs')[0]['data']['token_weights_visible'])
    def test_real_api_interface_mock_and_top_logprobs(self):
        client = FakeClient(FakeResponse(FakeLogprobs()))
        result = module.execute_neural_turn('INPUT: Tây Bắc', journal=self.logger, client=client)
        self.assertTrue(result.startswith('Trả lời'))
        self.assertEqual(client.calls[0]['top_logprobs'], 3)
        self.assertTrue(client.calls[0]['logprobs'])
        self.assertTrue(events(self.home, 'logprobs')[0]['data']['provider_returned'])
        self.assertEqual(events(self.home, 'raw')[0]['data']['direction'], 'INPUT')
        self.assertEqual(events(self.home, 'raw')[1]['wave'], 'ALPHA')
        self.assertNotIn('content', events(self.home, 'raw')[0]['data'])
    def test_logprobs_unavailable_not_fabricated(self):
        client = FakeClient(FakeResponse())
        module.execute_neural_turn('north', journal=self.logger, client=client)
        self.assertEqual(events(self.home, 'logprobs')[0]['status'], 'NOT_RETURNED')
    def test_provider_error_saved_without_exception_secrets(self):
        client = FakeClient(None, RuntimeError('sk-abc123abc123abc123'))
        with self.assertRaises(RuntimeError):
            module.execute_neural_turn('E', journal=self.logger, client=client)
        self.assertEqual(events(self.home, 'chrono')[-1]['data']['event'], 'TURN_FAILED')
        self.assertNotIn('sk-abc123', (self.home / module.LAYERS['temp']).read_text())
    def test_credential_redaction_opt_in(self):
        secret = 'sk-abcdef1234567890123456'
        module.execute_neural_turn('INPUT: Đông Bắc ' + secret, journal=self.logger, dry_run=True, capture_raw=True)
        data = events(self.home, 'raw')[0]['data']
        self.assertIn('[REDACTED_CREDENTIAL]', data['content'])
        self.assertNotIn(secret, data['content'])
    def test_no_false_spatial_inference(self):
        self.assertEqual(module.direction_view('Xin chào')['status'], 'NOT_A_SPATIAL_SIGNAL')
        self.assertEqual(module.direction_view('INPUT: Đông Bắc')['angle'], 45)

if __name__ == '__main__': unittest.main()
