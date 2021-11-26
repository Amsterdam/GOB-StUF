import os
from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from gobstuf.api import get_flask_app
from gobcore.secure.request import ACCESS_TOKEN_HEADER

BASE = 'tests'


def _env(var: str) -> str:
    return os.environ[var]


def _read_file(path: str) -> str:
    with open(path, mode='r') as file:
        return file.read()


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
    with app.test_client() as client:
        client.testing = True
        yield client


@pytest.fixture
def jwt_header() -> dict:
    return {ACCESS_TOKEN_HEADER: _read_file(f'{BASE}/utils/jwt.txt')}


@pytest.fixture(autouse=True)
def stuf_310_response(requests_mock):
    url = f"{_env('ROUTE_SCHEME')}://{_env('ROUTE_NETLOC')}{_env('ROUTE_PATH_310')}"
    mock_response = _read_file(f"{BASE}/response_310.xml")
    requests_mock.post(url, text=mock_response)
