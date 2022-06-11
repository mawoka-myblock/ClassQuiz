import uuid

import pytest
from redis import Redis
from classquiz.db import models
from classquiz.config import settings
from classquiz.tests import test_user_email, test_user_password
from classquiz.tests import test_client, example_quiz, ValueStorage  # noqa : F401


# @pytest.fixture
# async def startup_and_shutdown_server():
#     """Start server as test fixture and tear down after test"""
#     print("starting up")
#     server = UvicornTestServer()
#     await server.up()
#     print("Server up")
#     yield
#     await server.down()


class TestUsers:
    @pytest.mark.asyncio
    async def test_create_test_user(self, test_client):  # noqa : F811
        resp = test_client.post(
            "/api/v1/users/create",
            json={"email": test_user_email, "password": test_user_password, "username": "mawoka"},
        )
        assert resp.status_code == 200
        assert resp.json()["email"] == test_user_email
        resp = test_client.post(
            "/api/v1/users/create",
            json={"email": test_user_email, "password": test_user_password, "username": "mawoka"},
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
    async def test_verify_email(self, test_client):  # noqa : F811
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        assert resp.status_code == 401
        user = test_client.get(f"/api/v1/internal/testing/user/{test_user_email}?secret_key={settings().secret_key}")
        assert (test_client.get("/api/v1/users/verify/dasadsasdadsasdsaddassad")).status_code == 404

        test_client.get(f"/api/v1/users/verify/{user.json()['verify_key']}")
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_check(self, test_client):  # noqa : F811
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        token = resp.json()["access_token"]
        resp = test_client.get("/api/v1/users/check", cookies={"access_token": f"Bearer {token}"})
        assert resp.status_code == 200
        resp = test_client.get("/api/v1/users/check", cookies={"access_token": "Bearer dasasdasddasadsasdadssadsd"})
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_me(self, test_client):  # noqa : F811
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
    async def test_rememberme(self, test_client):  # noqa : F811
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        rememberme_token = resp.cookies["rememberme_token"]
        resp = test_client.get("/api/v1/users/token/rememberme", cookies={"rememberme_token": rememberme_token})
        assert resp.cookies["access_token"] is not None
        assert resp.status_code == 200
        resp = test_client.get(
            "/api/v1/users/token/rememberme", cookies={"rememberme_token": "dsahgvjadsvsahgxddsvhgdsvhg"}
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_logout(self, test_client):  # noqa : F811
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        rememberme_token = resp.cookies["rememberme_token"]
        access_token = resp.cookies["access_token"]
        resp = test_client.get("/api/v1/users/me", cookies={"access_token": access_token})
        assert resp.status_code == 200
        resp = test_client.get(
            "/api/v1/users/logout", cookies={"rememberme_token": rememberme_token}, allow_redirects=False
        )
        assert resp.status_code == 302
        resp = test_client.get("/api/v1/users/me", cookies={"rememberme_token": rememberme_token})
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_password_update(self, test_client):  # noqa : F811
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
        rememberme_token = resp1.cookies["rememberme_token"]
        response = test_client.get("/api/v1/users/me", cookies={"rememberme_token": rememberme_token})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_session(self, test_client):  # noqa : F811
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        token = resp.cookies["rememberme_token"]
        resp = test_client.get("/api/v1/users/session", cookies={"rememberme_token": token})
        assert resp.status_code == 200
        assert resp.json()["ip_address"] == "testclient"

    @pytest.mark.asyncio
    async def test_delete_session(self, test_client):  # noqa : F811
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        token = resp.cookies["rememberme_token"]
        resp = test_client.get("/api/v1/users/session", cookies={"rememberme_token": token})
        session_id = resp.json()["id"]
        resp = test_client.delete("/api/v1/users/sessions/" + str(session_id), cookies={"rememberme_token": token})
        assert resp.status_code == 200
        resp = test_client.delete("/api/v1/users/sessions/asdsadasdasdsad", cookies={"rememberme_token": token})
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_list_sessions(self, test_client):  # noqa : F811
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        token = resp.cookies["rememberme_token"]
        resp = test_client.get("/api/v1/users/sessions/list", cookies={"rememberme_token": token})
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    @pytest.mark.asyncio
    async def test_forgotten_password(self, test_client):  # noqa : F811
        resp = test_client.post("/api/v1/users/forgot-password", json={"email": test_user_email})
        assert resp.status_code == 200
        resp = test_client.post("/api/v1/users/forgot-password", json={"email": "ddassad@dsa.ads"})
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_reset_password_with_token(self, test_client):  # noqa : F811
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        token = resp.cookies["access_token"]
        me = test_client.get("/api/v1/users/me", cookies={"access_token": token}).json()
        redis = Redis().from_url(settings().redis)
        redis.set("reset_passwd:_1token_", str(me["id"]))
        redis.set("reset_passwd:_2token_", str(uuid.uuid4()))
        # test wtith wrong token
        resp = test_client.post(
            "/api/v1/users/reset-password", json={"token": "doesnt_exist", "password": "new_password"}
        )
        assert resp.status_code == 400
        resp = test_client.post("/api/v1/users/reset-password", json={"token": "_2token_", "password": "new_password"})
        assert resp.status_code == 400
        resp = test_client.post("/api/v1/users/reset-password", json={"token": "_1token_", "password": "new_password"})
        assert resp.status_code == 200
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": "new_password"}
        )
        token = resp.cookies["access_token"]
        test_client.put(
            "/api/v1/users/password/update",
            json={"new_password": test_user_password, "old_password": "new_password"},
            cookies={"access_token": token},
        )
        redis.flushdb()

    @pytest.mark.asyncio
    async def test_signout_everywhere(self, test_client):  # noqa : F811
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        token = resp.cookies["access_token"]
        resp = test_client.delete("/api/v1/users/signout-everywhere", cookies={"access_token": token})
        assert resp.status_code == 200


class TestUtils:
    @pytest.mark.asyncio
    async def test_get_ip_data(self, test_client):  # noqa : F811
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        token = resp.cookies["access_token"]
        resp = test_client.get("/api/v1/utils/ip-lookup/1.1.1.1", cookies={"access_token": token})
        assert resp.status_code == 200
        assert resp.json()["query"] == "1.1.1.1"

    @pytest.mark.asyncio
    async def test_get_qr(self, test_client):  # noqa : F811
        resp = test_client.get("/api/v1/utils/qr/12345678")
        assert resp.status_code == 200
        assert resp.headers["Content-Type"] == "image/svg+xml"


class TestStats:
    @pytest.mark.asyncio
    async def test_get_quiz_count(self, test_client):  # noqa : F811
        redis = Redis().from_url(settings().redis)
        redis.flushdb()
        for _ in range(2):
            resp = test_client.get("/api/v1/stats/quizzes")
            assert resp.status_code == 200
            assert resp.text == str(0)

    @pytest.mark.asyncio
    async def test_get_user_count(self, test_client):  # noqa : F811
        redis = Redis().from_url(settings().redis)
        redis.flushdb()
        for _ in range(2):
            resp = test_client.get("/api/v1/stats/users")
            assert resp.status_code == 200
            assert resp.text == str(1)

    @pytest.mark.asyncio
    async def test_get_combined_count(self, test_client):  # noqa : F811
        redis = Redis().from_url(settings().redis)
        redis.flushdb()
        for _ in range(2):
            resp = test_client.get("/api/v1/stats/combined")
            assert resp.status_code == 200
            assert resp.json()["quiz_count"] == 0
            assert resp.json()["user_count"] == 1


class TestQuiz:
    @pytest.mark.asyncio
    async def test_create_quiz(self, test_client):  # noqa : F811
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        token = resp.cookies["access_token"]

        resp = test_client.post("/api/v1/quiz/create", json=example_quiz, cookies={"access_token": token})
        assert resp.status_code == 200
        ValueStorage.quiz_id = resp.json()["id"]
        example_quiz["questions"][1]["image"] = "https://imgur.com/sSNSy77.png"
        resp = test_client.post("/api/v1/quiz/create", json=example_quiz, cookies={"access_token": token})
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_get_quiz_from_id(self, test_client):  # noqa : F811
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        token = resp.cookies["access_token"]
        resp = test_client.get(f"/api/v1/quiz/get/{ValueStorage.quiz_id}", cookies={"access_token": token})
        assert resp.status_code == 200
        resp = test_client.get("/api/v1/quiz/get/dasdsadsadsadsadsa", cookies={"access_token": token})
        assert resp.status_code == 400
        resp = test_client.get("/api/v1/quiz/get/847c64d3-39f9-4bb7-8f13-fae913f67858", cookies={"access_token": token})
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_list_quizzes(self, test_client):  # noqa : F811
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        token = resp.cookies["access_token"]
        resp = test_client.get("/api/v1/quiz/list", cookies={"access_token": token})
        assert resp.status_code == 200
        assert resp.json()[0]["id"] == ValueStorage.quiz_id

    @pytest.mark.asyncio
    async def test_update_quiz(self, test_client):  # noqa : F811
        example_quiz["public"] = True
        example_quiz["questions"][1]["image"] = "https://i.imgur.com/sSNSy77.png"
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        token = resp.cookies["access_token"]
        resp = test_client.put(
            f"/api/v1/quiz/update/{ValueStorage.quiz_id}", json=example_quiz, cookies={"access_token": token}
        )
        assert resp.status_code == 200
        resp = test_client.put(
            "/api/v1/quiz/update/f183e091-a863-44ec-a1b7-c70eb92e3f6a",
            json=example_quiz,
            cookies={"access_token": token},
        )
        assert resp.status_code == 404
        resp = test_client.put(
            "/api/v1/quiz/update/saddsaasddsadsa", json=example_quiz, cookies={"access_token": token}
        )
        assert resp.status_code == 400
        example_quiz["public"] = False
        test_client.put(
            f"/api/v1/quiz/update/{ValueStorage.quiz_id}", json=example_quiz, cookies={"access_token": token}
        )
        example_quiz["public"] = True
        test_client.put(
            f"/api/v1/quiz/update/{ValueStorage.quiz_id}", json=example_quiz, cookies={"access_token": token}
        )

    @pytest.mark.asyncio
    async def test_import_quiz(self, test_client):  # noqa : F811
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        token = resp.cookies["access_token"]
        resp = test_client.post(
            "/api/v1/quiz/import/1f95eb0b-fcf4-4db2-879b-5418ef75116b", cookies={"access_token": token}
        )
        assert resp.status_code == 200
        ValueStorage.imported_quizzes.append(resp.json()["id"])
        resp = test_client.post("/api/v1/quiz/import/1f95eb0bdassdadasdas", cookies={"access_token": token})
        assert resp.text == '"quiz not found"'

    @pytest.mark.asyncio
    async def test_get_public_quiz(self, test_client):  # noqa : F811
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        token = resp.cookies["access_token"]
        resp = test_client.get(f"/api/v1/quiz/get/public/{ValueStorage.imported_quizzes[0]}")
        assert resp.status_code == 200
        resp = test_client.get(
            "/api/v1/quiz/get/public/f183e091-a863-44ec-a1b7-c70eb92e3f6a", cookies={"access_token": token}
        )
        assert resp.status_code == 404
        resp = test_client.get("/api/v1/quiz/get/public/dadasdas92e3f6a", cookies={"access_token": token})
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_search_get(self, test_client):  # noqa : F811
        resp = test_client.get("/api/v1/search/?q=*")
        assert resp.status_code == 200
        assert len(resp.json()["hits"]) > 0

    @pytest.mark.asyncio
    async def test_search_post(self, test_client):  # noqa : F811
        resp = test_client.post("/api/v1/search/", json={"q": "*"})
        assert resp.status_code == 200
        assert len(resp.json()["hits"]) > 0

    @pytest.mark.asyncio
    async def test_image_cdn(self, test_client):  # noqa : F811
        resp = test_client.get(f"/api/v1/quiz/get/public/{ValueStorage.imported_quizzes[0]}")
        assert resp.status_code == 200
        quiz = resp.json()
        image_url = quiz["questions"][0]["image"]
        resp = test_client.get(image_url)
        assert resp.status_code == 200
        resp = test_client.get(f"{image_url}sadgvsadgvhsad")
        assert resp.status_code == 400


class TestPlayQuiz:
    @pytest.mark.asyncio
    async def test_start_quiz(self, test_client):  # noqa : F811
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        token = resp.cookies["access_token"]
        resp = test_client.post(
            "/api/v1/quiz/start/fb5adc91-629e-416e-8b98-ae400e36417c", cookies={"access_token": token}
        )
        assert resp.status_code == 404
        resp = test_client.post(
            "/api/v1/quiz/start/fb5adc91-629e-416e-8b98-ae400sdadsasadsadasddsae36417c", cookies={"access_token": token}
        )
        assert resp.status_code == 400
        resp = test_client.post(f"/api/v1/quiz/start/{ValueStorage.quiz_id}", cookies={"access_token": token})
        ValueStorage.game_pin = resp.json()["game_pin"]
        ValueStorage.game_id = resp.json()["game_id"]

    @pytest.mark.asyncio
    async def test_check_captcha_enabled(self, test_client):  # noqa : F811
        res = test_client.get(f"/api/v1/quiz/play/check_captcha/{ValueStorage.game_pin}")
        assert res.status_code == 200
        assert res.json()["enabled"] is True

        res = test_client.get("/api/v1/quiz/play/check_captcha/dsadsadas")
        assert res.status_code == 404

    @pytest.mark.asyncio
    async def test_join_game_route(self, test_client):  # noqa : F811
        res = test_client.get(f"/api/v1/quiz/join/{ValueStorage.game_pin}")
        assert res.status_code == 200
        assert res.text == f'"{ValueStorage.game_id}"'
        res = test_client.get("/api/v1/quiz/join/dsadasdasdas")
        assert res.status_code == 404


# skipcq: PYL-W0105
"""
class TestCache:
    @pytest.mark.asyncio
    async def test_cache_get_by_username(self, test_client):
        user = await get_user_from_username("mawoka")
        user = await get_user_from_username("mawoka")

    @pytest.mark.asyncio
    async def test_cache_get_by_id(self, test_client):
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        token = resp.cookies["access_token"]
        resp = test_client.get("/api/v1/users/me", cookies={"access_token": token})
        user = await get_user_from_id(resp.json()["id"])
"""


class TestDeleteStuff:
    @pytest.mark.asyncio
    async def test_delete_quiz(self, test_client):  # noqa : F811
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        token = resp.cookies["access_token"]
        resp = test_client.delete(
            f"/api/v1/quiz/delete/{ValueStorage.imported_quizzes[0]}", cookies={"access_token": token}
        )
        assert resp.status_code == 200
        resp = test_client.delete(
            "/api/v1/quiz/delete/be582c77-da03-4271-929c-5d582056eb78", cookies={"access_token": token}
        )
        assert resp.status_code == 404

        resp = test_client.delete(
            "/api/v1/quiz/delete/be582c77-da03-sdaasdadsasddas4271-929c-5d582056eb78", cookies={"access_token": token}
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_delete_user(self, test_client):  # noqa : F811
        resp = test_client.post(
            "/api/v1/users/token/cookie", data={"username": test_user_email, "password": test_user_password}
        )
        token = resp.cookies["access_token"]
        data = {"password": test_user_password}
        resp = test_client.delete("/api/v1/users/me", cookies={"access_token": token}, json=data)
        assert resp.status_code == 200
