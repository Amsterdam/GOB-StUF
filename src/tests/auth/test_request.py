from unittest import TestCase
from unittest.mock import patch

from gobstuf.auth.request import ACCESS_TOKEN_HEADER, extract_roles, is_secured_request, decode_token


class TestRequest(TestCase):

    @patch("gobstuf.auth.request.jwt")
    def test_extract_roles(self, mock_jwt):

        mock_jwt.decode.return_value = {
            'realm_access': {
                'roles': ['any roles']
            }
        }

        headers = {
            ACCESS_TOKEN_HEADER: "the token"
        }
        roles = extract_roles(headers)
        self.assertEqual(roles, ["any roles"])
        mock_jwt.decode.assert_called_with(
            'the token',
            options={'verify_signature': False},
            algorithms=["RS256", "HS256"]
        )

        roles = extract_roles({})
        self.assertEqual(roles, [])

    def test_decode_token(self):
        self.assertEqual({}, decode_token({ACCESS_TOKEN_HEADER: "token"}))

    def test_is_secured_request(self):
        self.assertTrue(is_secured_request({ACCESS_TOKEN_HEADER: 'access token'}))
        self.assertFalse(is_secured_request({}))
