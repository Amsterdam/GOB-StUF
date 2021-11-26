
class TestIngeschrevenpersonenBsnView:

    def test_adresseerbaar_object(self, client, jwt_header):
        response = client.get("/brp/ingeschrevenpersonen/123456789", headers=jwt_header)
        assert response.json['verblijfplaats']["adresseerbaarObjectIdentificatie"] == "0518010000784987"
