from collections import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from gobstuf.api import get_flask_app


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    """Creates a flask test app, with an app context.

    The app can be used to create a test http client as well:
    with app.test_client() as client:
        client.get(...)
    """
    # add app_config TestConfig here.
    app = get_flask_app()  # {"TESTING": True})
    with app.app_context():
        yield app


@pytest.fixture
def client(app: Flask) -> Generator[FlaskClient, None, None]:
    with app.test_client() as client:
        yield client
