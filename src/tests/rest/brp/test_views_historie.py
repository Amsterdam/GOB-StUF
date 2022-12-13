import pytest
from urllib.parse import urlencode


class TestIngeschrevenpersonenBsnViewHistorie:

    @pytest.mark.parametrize("stuf_310_response", ["response_310_historie.xml"], indirect=True)
    def test_historie_connection(self, stuf_310_response, app_base_path, client, jwt_header):
        """Make sure a connection can be made"""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789/verblijfsplaatshistorie", headers=jwt_header)
        assert response.status_code == 200

    bsn_err = {
        "min_len": "Waarde is korter dan minimale lengte 9",
        "max_len": "Waarde is langer dan maximale lengte 9",
        "no_int": "Waarde is geen geldige integer."
    }

    @pytest.mark.parametrize("bsn, status_code, msg", [
        ("undefined", 400, bsn_err["no_int"]),  # len == 9
        ("undefined1", 400, bsn_err["max_len"]),
        ("undefin1", 400, bsn_err["min_len"]),
        ("*********", 400, bsn_err["no_int"]),  # len == 9
        ("12345678", 400, bsn_err["min_len"]),
        ("1234567899", 400, bsn_err["max_len"]),
        ("١٢٣٤٥٦٧٨٩", 400, bsn_err["no_int"]),  # len == 9
        ("023456789", 200, ""),
        ("", 308, ""),
        ("/", 404, ""),
    ])
    def test_query_bsn(self, stuf_310_response, app_base_path, client, jwt_header, bsn, status_code, msg):
        """Test for different bsn queries and use the correct error message."""
        # https://github.com/VNG-Realisatie/Haal-Centraal-BRP-bevragen/issues/499
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/{bsn}/verblijfsplaatshistorie", headers=jwt_header)
        assert response.status_code == status_code

        if response.status_code == 400:
            assert response.json["invalid-params"][0]["reason"] == msg

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
