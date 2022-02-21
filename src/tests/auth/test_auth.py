from unittest import TestCase
from unittest.mock import patch, MagicMock

from gobstuf.auth.routes import secure_route, get_auth_url


class MockG:

    MKS_GEBRUIKER = None
    MKS_APPLICATIE = None


class MockRequest:

    headers = None


def view_func(*args, **kwargs):
    return "access_granted_" + ",".join(args) + "_" + str(kwargs)


class TestSecureRoute:

    def test_secure_route_allow(self, jwt_header, app):
        route_name = "route_name"

        with patch("gobstuf.auth.routes.request", MockRequest) as mock_request, \
                patch("gobstuf.auth.routes.g", MockG) as mock_g:
            mock_request.headers = jwt_header
            result = secure_route("rule", view_func, name=route_name)

            assert result.__name__ == route_name
            assert result("1", "2", kwarg="3") == "access_granted_1,2_{'kwarg': '3'}"
            assert mock_g.MKS_GEBRUIKER == "test_burger"
            assert mock_g.MKS_APPLICATIE == "fp_test_burger"

    def test_secure_route_forbidden(self, jwt_header_forbidden, app):
        route_name = "route_name"

        with patch("gobstuf.auth.routes.request", MockRequest) as mock_request, \
                patch("gobstuf.auth.routes.g", MockG) as mock_g:
            mock_request.headers = jwt_header_forbidden
            result = secure_route("rule", view_func, name=route_name)

            assert result.__name__ == route_name
            assert result("1", "2", kwarg="3") == ("Forbidden", 403)
            assert mock_g.MKS_GEBRUIKER is None
            assert mock_g.MKS_APPLICATIE is None


class TestAuth(TestCase):

    @patch('gobstuf.auth.routes.url_for')
    def test_get_auth_url(self, mock_url_for):
        mock_request = MagicMock()

        with patch('gobstuf.auth.routes.request', mock_request):
            view_name = 'any view'
            mock_request.scheme = 'http(s)'
            mock_request.host = 'any host'
            mock_request.base_url = ''

            mock_url_for.return_value = '/any url'

            result = get_auth_url(view_name)
            self.assertEqual(result, "http(s)://any host/any url")
            mock_url_for.assert_called_with('any view')
