import pytest


class TestIngeschrevenpersonenBsnView:

    def test_adresseerbaar_object(self, stuf_310_response, app_base_path, client, jwt_header, monkeypatch):
        """Asserts valid index and value in result of `adresseerbaarObjectIdentificatie` response."""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.status_code == 200
        assert list(response.json["verblijfplaats"])[1] == "adresseerbaarObjectIdentificatie"
        assert response.json["verblijfplaats"]["adresseerbaarObjectIdentificatie"] == "0518010000784987"

    @pytest.mark.parametrize("stuf_310_response", ["response_310_in_onderzoek.xml"], indirect=True)
    def test_in_onderzoek_true(self, stuf_310_response, app_base_path, client, jwt_header, monkeypatch):
        """Make sure inOnderzoek is set when it is in XML."""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.status_code == 200
        assert response.json["verblijfplaats"]["inOnderzoek"]

    @pytest.mark.parametrize("stuf_310_response", ["response_310.xml"], indirect=True)
    def test_in_onderzoek_false(self, stuf_310_response, app_base_path, client, jwt_header, monkeypatch):
        """Make sure inOnderzoek is not set when it is not in XML."""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.status_code == 200
        assert "inOnderzoek" not in response.json["verblijfplaats"]

