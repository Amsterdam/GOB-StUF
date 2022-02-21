import os
from pathlib import Path
from typing import Generator

import jwt
import pytest
from flask import Flask
from flask.testing import FlaskClient

from gobcore.secure.request import ACCESS_TOKEN_HEADER, USER_NAME_HEADER
from gobstuf.api import get_flask_app


def _env(var: str) -> str:
    return os.environ[var]


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    """Creates a flask test app, with an app context.

    The app can be used to create a test http client as well:
    with app.test_client() as client:
        client.get(...)
    """
    app = get_flask_app()
    with app.app_context():
        yield app


@pytest.fixture
def client(app: Flask) -> Generator[FlaskClient, None, None]:
    """Initiates Flask test client. Set testing to true to propagate errors."""
    with app.test_client() as client:
        client.testing = True
        yield client


@pytest.fixture
def tests_dir() -> Path:
    """Returns directory which contains tests. Used to find files required for tests."""
    old_dir = Path.cwd()
    test_dir = Path(__file__).parent

    try:
        os.chdir(test_dir.parent)
        yield test_dir
    finally:
        os.chdir(old_dir)


@pytest.fixture(params=[{"roles": ["fp_test_burger", "brp_r"], USER_NAME_HEADER: "test_burger"}])
def jwt_header(request) -> dict[str, bytes]:
    """
    Generates a jwt token with given roles. Allows authenticating test-requests.
    The request will fail with 403 if these are not in roles: `brp_r` and `fp_*`
    Preferred_username is optional in the request to MKS

    :param request: pytest SubRequest object.
    :return: A header dict containing a JWT token and preferred username.
    """
    header = {"type": "JWT", "alg": "RS256"}
    payload = {"realm_access": {"roles": request.param["roles"]}}
    return {
        ACCESS_TOKEN_HEADER: jwt.encode(payload, key='', headers=header),
        USER_NAME_HEADER: request.param[USER_NAME_HEADER],
        '_param': request.param
    }


@pytest.fixture(params=[
    {"roles": ["fp_test_burger_403", "brp_r_403"], USER_NAME_HEADER: "test_burger"},
    {"roles": ["brp_r"], USER_NAME_HEADER: "test_burger"},
    {"roles": ["fp_test_burger"], USER_NAME_HEADER: "test_burger"},
    {USER_NAME_HEADER: "test_burger"},
    {"roles": [], USER_NAME_HEADER: ""},
    {"roles": ["roles"]},
    {}
])
def jwt_header_forbidden(request) -> dict[str, bytes]:
    """
    Generates a jwt token with given roles. Allows authenticating test-requests.
    The request will fail with 403 if these are not in roles: `brp_r` and `fp_*`
    Preferred_username is optional in the request to MKS

    :param request: pytest SubRequest object.
    :return: A JWT token.
    """
    if not request.param:
        return {}

    header = {'_param': request.param}

    if "roles" in request.param:
        payload = {"realm_access": {"roles": request.param}}
        token_header = {"type": "JWT", "alg": "RS256"}
        header[ACCESS_TOKEN_HEADER] = jwt.encode(payload, key='', headers=token_header)

    if USER_NAME_HEADER in request.param:
        header[USER_NAME_HEADER] = request.param[USER_NAME_HEADER]

    return header


@pytest.fixture(params=["response_310.xml"])
def stuf_310_response(request, requests_mock, tests_dir: Path) -> None:
    """Mocks the response from the 310 stuf endpoint.
    This response is read from the `response_310.xml` file when no parameter is passed.

    :param request: pytest SubRequest object.
    :param requests_mock: a mock object to mock http responses.
    :param tests_dir: root directory which contains tests.
    """
    response_xml = request.param
    url = f"{_env('ROUTE_SCHEME')}://{_env('ROUTE_NETLOC')}{_env('ROUTE_PATH_310')}"
    mock_response = Path(tests_dir, "fixtures", response_xml).read_text()
    requests_mock.post(url, text=mock_response)


@pytest.fixture
def app_base_path() -> str:
    """Returns the base path where the api is mounted.

    For example:
        /gob_stuf_test

    :returns: the path as a string.
    """
    return os.environ['BASE_PATH']
