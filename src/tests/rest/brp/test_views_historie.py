import freezegun
import pytest
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

from gobstuf.stuf.message import StufMessage

class TestIngeschrevenpersonenBsnViewHistorie:

    @pytest.mark.parametrize("stuf_310_response", ["response_310_historie.xml"], indirect=True)
    def test_historie_connection(self, stuf_310_response, app_base_path, client, jwt_header):
        """Make sure a connection can be made"""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789/verblijfsplaatshistorie", headers=jwt_header)
        assert response.status_code == 200

    @pytest.mark.parametrize("stuf_310_response", ["response_310_historie.xml"], indirect=True)
    def test_historie_connection_too_long_bsn(self, stuf_310_response, app_base_path, client, jwt_header):
        """Make sure a connection can be made"""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/1234566789/verblijfsplaatshistorie", headers=jwt_header)
        assert response.status_code == 400

    @pytest.mark.parametrize("stuf_310_response", ["response_310_historie.xml"], indirect=True)
    def test_historie_connection_too_short(self, stuf_310_response, app_base_path, client, jwt_header):
        """Make sure a connection can be made"""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/12345667/verblijfsplaatshistorie", headers=jwt_header)
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "query_param, result_code, err_on",
        [
            ({
                 "peildatum": "2018-02-01"
             }, 200, None),
            ({}, 200, None),
            ({
                 "datumVan": "2000-02-01",
                 "datumTotEnMet": "2012-11-02"
             }, 200, None), 
             ({
                 "peildatum": "20005-02-01",
             }, 400, [
                 {"name": "peildatum", "code": "invalidFormat"}
             ]),
             ({
                 "peildatum": "2005-13-13",
             }, 400, [
                 {"name": "peildatum", "code": "invalidDate"}
             ])
        ]
    )
    def test_query_parameters(
            self, stuf_310_response, app_base_path, client, jwt_header, query_param, result_code, err_on
    ):
        """Test query parameters on the test client."""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789/verblijfsplaatshistorie?{urlencode(query_param)}", headers=jwt_header)
        assert response.status_code == result_code

        if invalid := response.json.get("invalid-params"):
            for inv, on in zip(invalid, err_on):
                assert inv["name"] == on["name"]
                assert inv["code"] == on["code"]
        else:
            assert response.json.get("invalid-params") is err_on



