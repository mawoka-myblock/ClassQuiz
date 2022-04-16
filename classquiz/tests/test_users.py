from typing import Generator

import pytest
from fastapi.testclient import TestClient
from classquiz.db import database, models


from classquiz import app

test_user_email = "sth@byom.de"
test_user_password = "test"


@pytest.fixture(scope="module")
def test_client() -> Generator:
    with TestClient(app) as testclient:
        yield testclient


def start_db():
    if not database.is_connected:
        database.connect()


@pytest.mark.asyncio
async def test_create_test_user(test_client):
    resp = test_client.post(
        "/api/v1/users/create", json={"email": test_user_email, "password": test_user_password, "username": "mawoka"}
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == test_user_email
    resp = test_client.post(
        "/api/v1/users/create", json={"email": test_user_email, "password": test_user_password, "username": "mawoka"}
    )
    assert resp.status_code == 409
    resp = test_client.post(
        "/api/v1/users/create",
        json={"email": "doesntexist@hidsadawadsdaads.ghsxd", "password": test_user_password, "username": "dieter"},
    )
    assert resp.status_code == 400

    resp = test_client.post(
        "/api/v1/users/create",
        json={
            "email": "doesntexist@hidsadawadsdaads.ghsxd",
            "password": test_user_password,
            "username": "12345678978978978978945632145678",
        },
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_verify_email(test_client):
    resp = test_client.post(
        "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
    )
    assert resp.status_code == 401
    user = await models.User.objects.filter(email=test_user_email).get()
    assert (test_client.get("/api/v1/users/verify/dasadsasdadsasdsaddassad")).status_code == 404

    test_client.get(f"/api/v1/users/verify/{user.verify_key}")
    resp = test_client.post(
        "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_check(test_client):
    resp = test_client.post(
        "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
    )
    token = resp.json()["access_token"]
    resp = test_client.get("/api/v1/users/check", cookies={"access_token": f"Bearer {token}"})
    assert resp.status_code == 200
    resp = test_client.get("/api/v1/users/check", cookies={"access_token": "Bearer dasasdasddasadsasdadssadsd"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me(test_client):
    resp = test_client.post(
        "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
    )
    token = resp.json()["access_token"]
    resp = test_client.get("/api/v1/users/me", cookies={"access_token": f"Bearer {token}"})
    data = resp.json()
    assert resp.status_code == 200
    assert data["verified"] is True
    assert data["email"] == test_user_email
    assert data["username"] == "mawoka"


@pytest.mark.asyncio
async def test_rememberme(test_client):
    resp = test_client.post(
        "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
    )
    rememberme_cookie = resp.cookies["rememberme_token"]
    resp = test_client.get("/api/v1/users/token/rememberme", cookies={"rememberme_token": rememberme_cookie})
    assert resp.cookies["access_token"] is not None
    assert resp.status_code == 200
    resp = test_client.get(
        "/api/v1/users/token/rememberme", cookies={"rememberme_token": "dsahgvjadsvsahgxddsvhgdsvhg"}
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_logout(test_client):
    resp = test_client.post(
        "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
    )
    rememberme_cookie = resp.cookies["rememberme_token"]
    access_token = resp.cookies["access_token"]
    resp = test_client.get("/api/v1/users/me", cookies={"access_token": access_token})
    assert resp.status_code == 200
    resp = test_client.get(
        "/api/v1/users/logout", cookies={"rememberme_cookie": rememberme_cookie}, allow_redirects=False
    )
    assert resp.status_code == 302
    resp = test_client.get("/api/v1/users/me", cookies={"rememberme_cookie": rememberme_cookie})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_password_update(test_client):
    resp = test_client.post(
        "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
    )
    token = resp.json()["access_token"]
    resp = test_client.put(
        "/api/v1/users/password/update",
        json={"new_password": "new_password", "old_password": test_user_password},
        cookies={"access_token": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    resp = test_client.put(
        "/api/v1/users/password/update",
        json={"new_password": "asdsdadsasdaasd", "old_password": "asdasdsadadsasdsadasdasd"},
        cookies={"access_token": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    resp = test_client.post(
        "/api/v1/users/token/cookie", data={"username": test_user_email, "password": "new_password"}
    )
    assert resp.status_code == 200
    resp = test_client.put(
        "/api/v1/users/password/update",
        json={"new_password": test_user_password, "old_password": "new_password"},
        cookies={"access_token": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    resp1 = test_client.post(
        "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
    )
    rememberme_cookie = resp1.cookies["rememberme_token"]
    response = test_client.get("/api/v1/users/me", cookies={"rememberme_cookie": rememberme_cookie})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_session(test_client):
    resp = test_client.post(
        "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
    )
    token = resp.cookies["access_token"]
    resp = test_client.get("/api/v1/users/session", cookies={"access_token": token})
    assert resp.status_code == 200
    assert resp.json()["ip_address"] == "testclient"


@pytest.mark.asyncio
async def test_delete_session(test_client):
    resp = test_client.post(
        "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
    )
    token = resp.cookies["access_token"]
    resp = test_client.get("/api/v1/users/session", cookies={"access_token": token})
    session_id = resp.json()["id"]
    resp = test_client.delete("/api/v1/users/sessions/" + str(session_id), cookies={"access_token": token})
    assert resp.status_code == 200
    resp = test_client.delete("/api/v1/users/sessions/asdsadasdasdsad", cookies={"access_token": token})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_list_sessions(test_client):
    resp = test_client.post(
        "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
    )
    token = resp.cookies["access_token"]
    resp = test_client.get("/api/v1/users/sessions/list", cookies={"access_token": token})
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
