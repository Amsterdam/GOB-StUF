import pytest


class TestIngeschrevenpersonenBsnView:

    def test_adresseerbaar_object(self, stuf_310_response, app_base_path, client, jwt_header):
        """Asserts valid index and value in result of `adresseerbaarObjectIdentificatie` response."""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.status_code == 200
        assert list(response.json["verblijfplaats"])[1] == "adresseerbaarObjectIdentificatie"
        assert response.json["verblijfplaats"]["adresseerbaarObjectIdentificatie"] == "0518010000784987"

    @pytest.mark.parametrize("stuf_310_response", ["response_310_in_onderzoek_j.xml"], indirect=True)
    def test_in_onderzoek_j(self, stuf_310_response, app_base_path, client, jwt_header):
        """Make sure inOnderzoek is set when it ha value J in XML."""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.status_code == 200
        assert response.json["verblijfplaats"]["inOnderzoek"]

    @pytest.mark.parametrize("stuf_310_response", ["response_310_in_onderzoek_n.xml"], indirect=True)
    def test_in_onderzoek_n(self, stuf_310_response, app_base_path, client, jwt_header):
        """Make sure inOnderzoek is not set when it has value N in XML."""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.status_code == 200
        assert "inOnderzoek" not in response.json["verblijfplaats"]

    @pytest.mark.parametrize("stuf_310_response", ["response_310.xml"], indirect=True)
    def test_in_onderzoek_missing(self, stuf_310_response, app_base_path, client, jwt_header):
        """Make sure inOnderzoek is not set when it is not in XML."""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.status_code == 200
        assert "inOnderzoek" not in response.json["verblijfplaats"]

    @pytest.mark.parametrize(
        "stuf_310_response",
        ["response_310_verblijfstitel_verkrijging_aanduiding.xml"],
        indirect=True
    )
    def test_verblijfstitel(self, stuf_310_response, app_base_path, client, jwt_header):
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.status_code == 200
        verblijfstitel = response.json["verblijfstitel"]
        assert verblijfstitel["datumIngang"]["datum"] == "2010-08-12"
        assert verblijfstitel["aanduiding"]["omschrijving"].startswith("Vw 2000 art. 8")

    @pytest.mark.parametrize("stuf_310_response", ["response_310.xml"], indirect=True)
    def test_verblijfstitel_none_when_datumVerliesVerblijfstitel(
            self, stuf_310_response, app_base_path, client, jwt_header
    ):
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.status_code == 200
        assert "verblijfstitel" not in response.json

    @pytest.mark.parametrize("stuf_310_response", ["response_310_verblijfstitel_incomplete.xml"], indirect=True)
    def test_verblijfstitel_none_on_incomplete_data(self, stuf_310_response, app_base_path, client, jwt_header):
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.status_code == 200
        assert "verblijfstitel" not in response.json
