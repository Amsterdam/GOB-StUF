import pytest
from urllib.parse import urlencode


class TestIngeschrevenpersonenBsnViewHistorie:

    @pytest.mark.parametrize("stuf_310_response", ["response_310_historie.xml"], indirect=True)
    def test_historie_connection(self, stuf_310_response, app_base_path, client, jwt_header):
        """Make sure a connection can be made"""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789/verblijfplaatshistorie", headers=jwt_header)
        assert response.status_code == 200

    @pytest.mark.parametrize("stuf_310_response", ["response_310_historie.xml"], indirect=True)
    def test_historie_connection_too_long_bsn(self, stuf_310_response, app_base_path, client, jwt_header):
        """Make sure a connection can't be made when the bsn is too long"""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/1234566789/verblijfplaatshistorie", headers=jwt_header)
        assert response.status_code == 400

    @pytest.mark.parametrize("stuf_310_response", ["response_310_historie.xml"], indirect=True)
    def test_historie_connection_too_short(self, stuf_310_response, app_base_path, client, jwt_header):
        """Make sure a connection can't be made with a too short bsn"""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/12345667/verblijfplaatshistorie", headers=jwt_header)
        assert response.status_code == 400

    @pytest.mark.parametrize("stuf_310_response", ["response_310_historie.xml"], indirect=True)
    def test_response_list_of_dict(self, stuf_310_response, app_base_path, client, jwt_header):
        """Test the return types."""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789/verblijfplaatshistorie", headers=jwt_header)
        objs = response.json["_embedded"]["verblijfplaatshistorie"]
        assert response.status_code == 200
        assert isinstance(objs, list) and all(isinstance(obj, dict) for obj in objs)

    @pytest.mark.parametrize("stuf_310_response", ["response_310_historie.xml"], indirect=True)
    @pytest.mark.parametrize(
        "query_param, result_code, err_on",
        [
            ({"datumVan": "1900-02-01", "peildatum": "2018-02-01"}, 200, None),
            ({}, 200, None),
            ({"datumTotEnMet": "2000-02-01"}, 200, None),
            ({"datumVan": "2000-02-01"}, 200, None),
            ({'datumVan': "2020-02-01", 'datumTotEnMet': '1990-01-01'}, 200, None),
            ({"peildatum": "2018-02-01"}, 200, None),
            ({}, 200, None),
            ({"datumVan": "2000-02-01", "datumTotEnMet": "2012-11-02"}, 200, None),
            ({"peildatum": "20005-02-01"}, 400, [{"name": "peildatum", "code": "invalidFormat"}]),
            ({"peildatum": "2005-13-13"}, 400, [{"name": "peildatum", "code": "invalidDate"}])
        ]
    )
    def test_query_parameters(
            self, stuf_310_response, app_base_path, client, jwt_header, query_param, result_code, err_on
    ):
        """Test query parameters on the test client."""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789/verblijfplaatshistorie?{urlencode(query_param)}", headers=jwt_header)
        assert response.status_code == result_code

        if invalid := response.json.get("invalid-params"):
            for inv, on in zip(invalid, err_on):
                assert inv["name"] == on["name"]
                assert inv["code"] == on["code"]
        else:
            assert response.json.get("invalid-params") is err_on

    @pytest.mark.parametrize("stuf_310_response", ["response_310_historie_overleden.xml"], indirect=True)
    def test_historie_overleden_empty_response(self, stuf_310_response, app_base_path, client, jwt_header):
        """Test returning empty list if person has indicatie overleden."""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789/verblijfplaatshistorie", headers=jwt_header)
        assert response.status_code == 200
        assert response.json["_embedded"]["verblijfplaatshistorie"] == []

    @pytest.mark.parametrize("stuf_310_response", ["response_310_empty.xml"], indirect=True)
    def test_historie_empty_404(self, stuf_310_response, app_base_path, client, jwt_header):
        """Test status 404 on empty response."""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789/verblijfplaatshistorie", headers=jwt_header)
        assert response.status_code == 404
        assert "Verblijfplaatshistorie niet gevonden voor burgerservicenummer 123456789." == response.json["detail"]

    @pytest.mark.parametrize("stuf_310_response", ["response_310_historie.xml"], indirect=True)
    def test_historie_filter_empty(self, stuf_310_response, app_base_path, client, jwt_header):
        """Test status 200 on empty response after filtering."""
        url =  f"{app_base_path}/brp/ingeschrevenpersonen/123456789/verblijfplaatshistorie?peildatum=1500-03-03"
        response = client.get(url, headers=jwt_header)

        assert response.status_code == 200
        assert response.json["_embedded"]["verblijfplaatshistorie"] == []
