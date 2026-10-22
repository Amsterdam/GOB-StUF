import json
from unittest import TestCase
from unittest.mock import MagicMock, patch

from gobstuf.rest.brp.rest_response import RESTResponse

mock_request = MagicMock()
mock_request.url = "https://flask.palletsprojects.com/"

test_data = {"test": "data"}


class TestRESTResponse(TestCase):
    """Test REST responses."""

    def test_json_response(self):
        """Test JSON responses."""
        with patch("gobstuf.rest.brp.rest_response.request", mock_request):
            response = RESTResponse._json_response(test_data)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.headers.get("Content-Type"), "application/json")
            self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
            self.assertEqual(json.loads(response.data), test_data)

            # Change mimetype in Response.
            response = RESTResponse._json_response(test_data, mimetype="application/hal+json")
            self.assertEqual(response.content_type, "application/hal+json")
            self.assertEqual(response.headers.get("Content-Security-Policy"), "default-src 'self'")

    def test_hal(self):
        """Test HAL data."""
        with patch("gobstuf.rest.brp.rest_response.request", mock_request):
            self.assertEqual(
                RESTResponse._hal(test_data),
                {"_links": {"self": {"href": "https://flask.palletsprojects.com/"}}, "test": "data"},
            )

    def test_client_error(self):
        """Test client error (4xx) responses."""
        with patch("gobstuf.rest.brp.rest_response.request", mock_request):
            response = RESTResponse._client_error_response(data=test_data, status=401)
            response_data = json.loads(response.data)

            # Check if all required attributes are present in the response data
            self.assertTrue(
                set(response_data.keys()).issuperset(("type", "title", "status", "detail", "instance", "code"))
            )
            self.assertEqual(response_data["instance"], mock_request.url)

            # Check if the type is correctly build
            self.assertEqual(
                response_data["type"],
                "https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.2 401 Unauthorized",
            )

            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.status, "401 UNAUTHORIZED")
            self.assertEqual(response.content_type, "application/problem+json")

            # Check valid overrides of default fields
            response = RESTResponse._client_error_response(data=test_data, status=403)
            response_data = json.loads(response.data)

            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.status, "403 FORBIDDEN")
            self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")

    def test_rest_ok(self):
        """Test OK response."""
        with patch("gobstuf.rest.brp.rest_response.request", mock_request):
            response = RESTResponse.ok(test_data)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/hal+json")
            self.assertEqual(response.headers.get("Content-Type"), "application/hal+json")

            self.assertEqual(response.json["test"], "data")
            self.assertEqual(response.json, RESTResponse._hal(test_data))

            # Check Security Headers
            self.assertEqual(response.headers.get("Content-Security-Policy"), "default-src 'self'")
            self.assertEqual(
                response.headers.get("Strict-Transport-Security"), "max-age=63072000; includeSubDomains; preload"
            )
            self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")
            self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")

    def test_bad_request(self):
        """Test bad request (400) response."""
        with patch("gobstuf.rest.brp.rest_response.request", mock_request):
            response = RESTResponse.bad_request()

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.status, "400 BAD REQUEST")
            self.assertEqual(response.content_type, "application/problem+json")
            self.assertEqual(response.json["status"], 400)
            self.assertEqual(
                response.json["detail"],
                "The request could not be understood by the server due to malformed syntax."
                " The client SHOULD NOT repeat the request without modification.",
            )
            self.assertEqual(
                response.headers.get("Strict-Transport-Security"), "max-age=63072000; includeSubDomains; preload"
            )

    def test_forbidden(self):
        """Test forbidden (403) response."""
        with patch("gobstuf.rest.brp.rest_response.request", mock_request):
            response = RESTResponse.forbidden()

            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.status, "403 FORBIDDEN")
            self.assertEqual(response.content_type, "application/problem+json")
            self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")

    def test_not_found(self):
        """Test not_found (404) response."""
        with patch("gobstuf.rest.brp.rest_response.request", mock_request):
            response = RESTResponse.not_found()

            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.status, "404 NOT FOUND")
            self.assertEqual(response.content_type, "application/problem+json")
            self.assertEqual(response.headers.get("Content-Security-Policy"), "default-src 'self'")

    def test_internal_server_error(self):
        """Test internal_server_error (500) response."""
        with patch("gobstuf.rest.brp.rest_response.request", mock_request):
            response = RESTResponse.internal_server_error()

            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.status, "500 INTERNAL SERVER ERROR")
            self.assertEqual(response.content_type, "application/problem+json")
            self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")
