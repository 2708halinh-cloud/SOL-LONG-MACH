"""Offline tests; no network requests."""
import unittest
from unittest.mock import MagicMock
import llm_tool as t


class TestLLMTool(unittest.TestCase):
    def test_contract(self):
        c = t.config()
        self.assertIn('TOOL', c['llm_role'])
        self.assertIn('CHAT', c['chat_role'])
        self.assertIn('NEUTRON (0)', c['tam_source'])

    def test_select_never_claims_live(self):
        v = t.select('ollama_local', {})
        self.assertFalse(v['callable_verified'])
        self.assertFalse(v['executed'])
        self.assertTrue(v['url_configured'])
        self.assertFalse(v['model_configured'])

    def test_payload(self):
        self.assertEqual(t.payload('ollama_local','qwen','hello')['prompt'], 'hello')
        self.assertEqual(t.payload('openai_compatible','model','hello')['messages'][0]['content'], 'hello')

    def test_url_allowlist(self):
        self.assertEqual(t.target_url('http://127.0.0.1:11434','ollama_local'),'http://127.0.0.1:11434/api/generate')
        self.assertEqual(t.target_url('https://example.net/v1','openai_compatible'),'https://example.net/v1/chat/completions')
        with self.assertRaises(ValueError):
            t.target_url('http://example.net','openai_compatible')
        with self.assertRaises(ValueError):
            t.target_url('https://me:password@example.net','openai_compatible')

    def test_missing_key_without_execution(self):
        with self.assertRaisesRegex(ValueError,'SECRET'):
            t.invoke('openai_compatible','hello',{'SOL_LLM_API_URL':'https://example.net/v1','SOL_LLM_MODEL':'foo'})

    def test_mock_provider_response_not_action(self):
        resp = MagicMock()
        resp.__enter__.return_value.read.return_value = b'{"response":"suggestion"}'
        opener = MagicMock(return_value=resp)
        data = t.invoke('ollama_local','hello',{'SOL_OLLAMA_MODEL':'test'},opener=opener)
        self.assertEqual(data['text'],'suggestion')
        self.assertEqual(data['role'],'LLM_TOOL_PROPOSAL_NOT_VERIFIED')
        opener.assert_called_once()

    def test_invalid_engine(self):
        with self.assertRaisesRegex(ValueError,'UNREGISTERED'):
            t.select('unsupported')


if __name__ == '__main__':
    unittest.main()
