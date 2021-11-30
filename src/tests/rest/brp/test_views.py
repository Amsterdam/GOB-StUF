import os

import pytest
from flask import Response


@pytest.fixture
def response(client, jwt_header, monkeypatch) -> Response:
    """Generates response for the ingeschrevenpersonen view."""
    base_path = os.environ['BASE_PATH']
    return client.get(f"{base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)


class TestIngeschrevenpersonenBsnView:

    def test_adresseerbaar_object(self, response: Response):
        """Asserts valid index and value in result of `adresseerbaarObjectIdentificatie` response."""
        assert list(response.json['verblijfplaats'])[1] == "adresseerbaarObjectIdentificatie"
        assert response.json['verblijfplaats']["adresseerbaarObjectIdentificatie"] == "0518010000784987"
