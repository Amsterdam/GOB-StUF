import os
from pathlib import Path
from typing import Generator

import jwt
import pytest
from flask import Flask
from flask.testing import FlaskClient

from gobcore.secure.request import ACCESS_TOKEN_HEADER
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


@pytest.fixture(params=[["fp_test_burger", "brp_r"]])
def jwt_header(request) -> dict[str, bytes]:
    """
    Generates a jwt token with given roles. Allows authenticating test-requests.
    The request will fail with 403 if these are not in roles: `brp_r` and `fp_*`

    :param request: pytest SubRequest object.
    :return: A JWT token.
    """
    header = {"type": "JWT", "alg": "RS256"}
    payload = {"realm_access": {"roles": request.param}}
    return {ACCESS_TOKEN_HEADER: jwt.encode(payload, key='', headers=header)}


@pytest.fixture(params=[["fp_test_burger_403", "brp_r_403"], ["brp_r"], ["fp_test_burger"]])
def jwt_header_forbidden(request) -> dict[str, bytes]:
    """
    Generates a jwt token with given roles. Allows authenticating test-requests.
    The request will fail with 403 if these are not in roles: `brp_r` and `fp_*`

    :param request: pytest SubRequest object.
    :return: A JWT token.
    """
    header = {"type": "JWT", "alg": "RS256"}
    payload = {"realm_access": {"roles": request.param}}
    return {ACCESS_TOKEN_HEADER: jwt.encode(payload, key='', headers=header)}


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
