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
    return Path(__file__).parent


@pytest.fixture(params=[["fp_test_burger", "brp_r"]])
def jwt_header(request) -> dict[str, bytes]:
    """Generates a jwt token with given roles. Allows authenticating test-requests."""
    header = {"type": "JWT", "alg": "RS256"}
    payload = {"realm_access": {"roles": request.param}}
    return {ACCESS_TOKEN_HEADER: jwt.encode(payload, key='', headers=header)}


@pytest.fixture(autouse=True)
def stuf_310_response(requests_mock, tests_dir: Path):
    """Mocks the response from the 310 stuf endpoint. This response is read from the `response_310.xml` file."""
    url = f"{_env('ROUTE_SCHEME')}://{_env('ROUTE_NETLOC')}{_env('ROUTE_PATH_310')}"
    mock_response = Path(tests_dir, "response_310.xml").read_text()
    requests_mock.post(url, text=mock_response)
