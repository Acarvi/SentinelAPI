import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from urllib.error import URLError, HTTPError

# Add SentinelAPI to path so we can import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sentinel_dir = os.path.abspath(os.path.join(current_dir, ".."))
if sentinel_dir not in sys.path:
    sys.path.insert(0, sentinel_dir)

from api_checker import verify_gemini_api, validate_all_apis
from security_audit import scan_for_secrets, check_gitignore

class TestSentinelAPI(unittest.TestCase):
    
    def setUp(self):
        # Ensure we are in a predictable directory for gitignore tests
        self.test_dir = os.getcwd()

    @patch('urllib.request.urlopen')
    def test_verify_gemini_api_success(self, mock_urlopen):
        """Test verify_gemini_api with a successful 200 response."""
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        with patch.dict(os.environ, {"GEMINI_API_KEY": "AIzaSyTestKey_12345678901234567890123"}):
            self.assertTrue(verify_gemini_api())

    @patch('urllib.request.urlopen')
    def test_verify_gemini_api_http_error(self, mock_urlopen):
        """Test verify_gemini_api with a 400 HTTP error."""
        mock_urlopen.side_effect = HTTPError("url", 400, "Bad Request", {}, None)
        
        with patch.dict(os.environ, {"GEMINI_API_KEY": "InvalidKey"}):
            self.assertFalse(verify_gemini_api())

    @patch('urllib.request.urlopen')
    def test_verify_gemini_api_network_error(self, mock_urlopen):
        """Test verify_gemini_api with a network/URL error."""
        mock_urlopen.side_effect = URLError("DNS Failure")
        
        with patch.dict(os.environ, {"GEMINI_API_KEY": "SomeKey"}):
            self.assertFalse(verify_gemini_api())

    def test_verify_gemini_api_missing_key(self):
        """Test verify_gemini_api when GEMINI_API_KEY is not in environment."""
        with patch.dict(os.environ, {}, clear=True):
            # We don't clear the whole environ as it might break things, 
            # just ensure the key is gone.
            if "GEMINI_API_KEY" in os.environ:
                del os.environ["GEMINI_API_KEY"]
            self.assertFalse(verify_gemini_api())

    @patch('security_audit.os.walk')
    def test_scan_for_secrets_detection(self, mock_walk):
        """Test that secret scanner detects a hardcoded Gemini key."""
        # Mock a file containing a secret
        mock_walk.return_value = [
            ('.', [], ['malicious.py'])
        ]
        
        # We need to mock open() to return our secret string
        # Regex: AIzaSy[A-Za-z0-9_-]{33} -> 6 + 33 = 39 characters
        mock_secret = 'AIzaSy' + 'A' * 33
        with patch('builtins.open', unittest.mock.mock_open(read_data=f'key = "{mock_secret}"')):
            # scan_for_secrets returns True if NO secrets found, False if found
            self.assertFalse(scan_for_secrets())

    def test_check_gitignore_presence(self):
        """Basic check that gitignore auditor returns bool."""
        # This will depend on the current workspace state
        result = check_gitignore()
        self.assertIsInstance(result, bool)

if __name__ == '__main__':
    unittest.main()
