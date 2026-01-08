import unittest
from unittest.mock import patch, MagicMock
from FastWrite import doc_generator

class TestDocGenerator(unittest.TestCase):
    @patch('requests.post')
    def test_generate_documentation_ollama(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Mocked documentation"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = doc_generator.generate_documentation_ollama("code", "prompt")
        self.assertEqual(result, "Mocked documentation")
        mock_post.assert_called_once()

    @patch('FastWrite.doc_generator.OpenAI')
    @patch('FastWrite.doc_generator.get_openai_api_key', return_value="fake_key")
    def test_generate_documentation_openai(self, mock_get_key, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Mocked OpenAI doc"
        mock_client.chat.completions.create.return_value = mock_response
        
        result = doc_generator.generate_documentation_openai("code", "prompt", openai_api_key="fake_key")
        self.assertEqual(result, "Mocked OpenAI doc")
