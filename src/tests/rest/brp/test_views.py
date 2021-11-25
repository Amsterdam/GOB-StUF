
class TestIngeschrevenpersonenBsnView:

    def test_get_with_bsn(self, app, client, requests_mock):
        bsn = "123"
        response = client.get(f"/brp/ingeschrevenpersonen/{bsn}")
        print(response)
        # assert response.json()["xyz"] == "blabla"
