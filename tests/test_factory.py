from tjts5901.app import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_language(client):
    with client.get("/", headers={'Accept-Language': 'en_US'}) as response:
        assert response.status_code == 200

        assert b"Get started by logging in or registering" in response.data