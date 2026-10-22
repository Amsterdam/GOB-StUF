import unittest
from unittest.mock import call, patch

from gobstuf.certrequest import cert_get, cert_post


class MockResponse:

    def __init__(self, status_code=0, reason=""):
        self.status_code = status_code
        self.reason = reason


@patch("gobstuf.certrequest.logger")
class TestConfig(unittest.TestCase):
    """Test if requests get certificate config from environment"""

    @patch("gobstuf.certrequest.requests")
    def test_get(self, mock_requests, mock_logger):
        mock_requests.get.return_value = MockResponse(200, "OK")

        cert_get("my_url", key="value")

        mock_requests.get.assert_called_once_with("my_url", cert=("cert.crt", "cert.key"), key="value")
        mock_logger.info.assert_has_calls([call("GET my_url"), call("RESPONSE 200, OK")])

    @patch("gobstuf.certrequest.requests")
    def test_post(self, mock_requests, mock_logger):
        mock_requests.post.return_value = MockResponse(200, "OK")

        cert_post("my_url", data="<xml>", key="value")

        mock_requests.post.assert_called_once_with("my_url", "<xml>", cert=("cert.crt", "cert.key"), key="value")
        mock_logger.info.assert_has_calls([call("POST my_url"), call("RESPONSE 200, OK")])
