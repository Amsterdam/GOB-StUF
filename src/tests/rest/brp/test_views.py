from pathlib import Path

import pytest
from flask import Response


@pytest.fixture
def response(client, jwt_header, monkeypatch) -> Response:
    return client.get("/brp/ingeschrevenpersonen/123456789", headers=jwt_header)


class TestIngeschrevenpersonenBsnView:

    def test_adresseerbaar_object(self, response: Response):
        assert response.json['verblijfplaats']["adresseerbaarObjectIdentificatie"] == "0518010000784987"
