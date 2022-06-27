import freezegun
import pytest
from urllib.parse import urlencode


class TestIngeschrevenpersonenBsnView:

    @pytest.mark.parametrize("key_path,expected", [
        (["verblijfplaats", "adresseerbaarObjectIdentificatie"], "0518010000784987"),
        (["nationaliteiten"], [{'nationaliteit': {'code': '0315'}}])
    ])
    def test_various_keys(self, key_path, expected, stuf_310_response, app_base_path, client, jwt_header):
        """Asserts if various keys are found in the correct 310 response."""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.status_code == 200

        def follow_key_path(val: dict, k_path: list[str]):
            for k in k_path:
                val = val.get(k, {})
            return val

        assert follow_key_path(response.json, key_path) == expected

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

    @pytest.mark.parametrize("stuf_310_response", ["response_310.xml"], indirect=True)
    def test_verblijfstitel_none_when_datumVerliesVerblijfstitel_in_past(
            self, stuf_310_response, app_base_path, client, jwt_header
    ):
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.status_code == 200
        assert "verblijfstitel" not in response.json

    @pytest.mark.parametrize("stuf_310_response", ["response_310.xml"], indirect=True)
    @freezegun.freeze_time("2011-01-01")
    def test_verblijfstitel_when_datumVerliesVerblijfstitel_in_future(
            self, stuf_310_response, app_base_path, client, jwt_header
    ):
        """Test if verblijfstitel is there when datum_verlies is in the future.

        Test date is 20110412 in response_310.xml.
        """
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.status_code == 200
        verblijfstitel = response.json["verblijfstitel"]
        assert verblijfstitel["datumEinde"]["datum"] == "2011-04-12"

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

    @pytest.mark.parametrize(
        "stuf_310_response",
        ["response_310_verblijfstitel_inonderzoek_j.xml"],
        indirect=True
    )
    def test_verblijfstitel_inonderzoek_j(self, stuf_310_response, app_base_path, client, jwt_header):
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.status_code == 200
        verblijfstitel = response.json["verblijfstitel"]
        assert verblijfstitel["inOnderzoek"]["aanduiding"] is True
        assert verblijfstitel["inOnderzoek"]["datumIngang"] is True
        assert verblijfstitel["inOnderzoek"]["datumEinde"] is True

    @pytest.mark.parametrize(
        "stuf_310_response",
        ["response_310_verblijfstitel_inonderzoek_n.xml"],
        indirect=True
    )
    def test_verblijfstitel_inonderzoek_n(self, stuf_310_response, app_base_path, client, jwt_header):
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.status_code == 200
        assert "inOnderzoek" not in response.json["verblijfstitel"]

    @pytest.mark.parametrize(
        "stuf_310_response",
        ["response_310_verblijfstitel_verkrijging_aanduiding.xml"],
        indirect=True
    )
    def test_verblijfstitel_inonderzoek_missing(self, stuf_310_response, app_base_path, client, jwt_header):
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.status_code == 200
        assert "inOnderzoek" not in response.json["verblijfstitel"]

    @pytest.mark.parametrize("stuf_310_response", ["response_310_verblijfstitel_incomplete.xml"], indirect=True)
    def test_verblijfstitel_none_on_incomplete_data(self, stuf_310_response, app_base_path, client, jwt_header):
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.status_code == 200
        assert "verblijfstitel" not in response.json

    @pytest.mark.parametrize(
        "stuf_310_response",
        ["response_310_nationaliteit_niet_geautoriseerd.xml"],
        indirect=True
    )
    def test_nationaliteit_unauthorized(self, stuf_310_response, app_base_path, client, jwt_header):
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.status_code == 200
        assert "nationaliteiten" not in response.json

    @pytest.mark.parametrize("stuf_310_response", ["response_310_nationaliteit_io.xml"], indirect=True)
    def test_nationaliteit_inonderzoek(self, stuf_310_response, app_base_path, client, jwt_header):
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        expected = {"nationaliteit": True, "aanduidingBijzonderNederlanderschap": True, "datumIngangGeldigheid": True}
        assert response.status_code == 200
        assert response.json["nationaliteiten"][0]["inOnderzoek"] == expected

    def test_anummer(self, stuf_310_response, app_base_path, client, jwt_header):
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.status_code == 200
        assert response.json["aNummer"] == "9794354356"

    @pytest.mark.parametrize("stuf_310_response", ["response_310.xml"], indirect=True)
    def test_forbidden_403(self, stuf_310_response, app_base_path, client, jwt_header_forbidden):
        """Test against an unauthorized jwt header."""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/123456789", headers=jwt_header_forbidden)
        assert response.status_code == 403
        assert response.data == b'Forbidden'

    @pytest.mark.parametrize(
        "query_param, result_code, err_on",
        [
            ({
                 "verblijfplaats__postcode": "1024QQ",
                 "verblijfplaats__huisnummer": "10",
                 "verblijfplaats__huisnummertoevoeging": "ABCD"
             }, 200, None),
            ({
                 "verblijfplaats__postcode": "1024QQ",
                 "verblijfplaats__huisnummer": "10",
                 "verblijfplaats__huisnummertoevoeging": "ABCDE"
             }, 400, [{"name": "verblijfplaats__huisnummertoevoeging", "code": "maxLength"}]),
            ({
                 "verblijfplaats__postcode": "1024QQQ",
                 "verblijfplaats__huisnummer": "10",
             }, 400, [{"name": "verblijfplaats__postcode", "code": "pattern"}]),
            ({
                 "verblijfplaats__postcode": "1024QQ",
                 "verblijfplaats__huisnummer": "A",
             }, 400, [{"name": "verblijfplaats__huisnummer", "code": "integer"}]),
            ({
                 "verblijfplaats__postcode": "1024QQ",
                 "verblijfplaats__huisnummer": "A",
                 "burgerservicenummer": "12345658"
             }, 400, [
                {"name": "burgerservicenummer", "code": "minLength"},
                {"name": "verblijfplaats__huisnummer", "code": "integer"}
            ])
        ]
    )
    def test_query_parameters(
            self, stuf_310_response, app_base_path, client, jwt_header, query_param, result_code, err_on
    ):
        """Test query parameters on the test client."""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen?{urlencode(query_param)}", headers=jwt_header)
        assert response.status_code == result_code

        if invalid := response.json.get("invalid-params"):
            for inv, on in zip(invalid, err_on):
                assert inv["name"] == on["name"]
                assert inv["code"] == on["code"]
        else:
            assert response.json.get("invalid-params") is err_on

    @pytest.mark.parametrize("bsn, status_code", [
        ("undefined", 400),
        ("********", 400),
        ("123456789", 200),
        ("023456789", 200)
    ])
    def test_query_bsn(self, stuf_310_response, app_base_path, client, jwt_header, bsn, status_code):
        """Test against an unauthorized jwt header."""
        response = client.get(f"{app_base_path}/brp/ingeschrevenpersonen/{bsn}", headers=jwt_header)
        assert response.status_code == status_code
