# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0


import uuid

import pytest
from redis import Redis
from frogquiz.config import settings
from frogquiz.tests import test_user_email, test_user_password, example_quiztivity
from frogquiz.tests import test_client, example_quiz, ValueStorage  # noqa : F401
from fastapi.testclient import TestClient
from frogquiz.db.models import ABCDQuizAnswer
from frogquiz.socket_server.helpers import check_check_question

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
    @staticmethod
    def log_in(tc: TestClient, email=test_user_email, password=test_user_password) -> int:
        resp = tc.post("/api/v1/login/start", json={"email": email})
        session_id = resp.json()["session_id"]
        resp = tc.post(
            f"/api/v1/login/step/1?session_id={session_id}", json={"auth_type": "PASSWORD", "data": password}
        )
        ValueStorage.cookies = resp.cookies
        return resp.status_code

    @pytest.mark.asyncio
    async def test_create_test_user(self, test_client: TestClient):  # noqa : F811
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
        # Addresses are one account whatever the casing. They used to be compared
        # byte for byte, so this was a second account -- and only one of the two was
        # reachable by the reset and resend lookups, while both got the same neutral
        # "a link is on its way" that exists so neither can be told apart.
        resp = test_client.post(
            "/api/v1/users/create",
            json={"email": test_user_email.upper(), "password": test_user_password, "username": "mawoka2"},
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
    async def test_verify_email(self, test_client: TestClient):  # noqa : F811
        user = test_client.get(f"/api/v1/internal/testing/user/{test_user_email}?secret_key={settings().secret_key}")
        # A wrong or superseded key is the commonest way to land here with an actual
        # error -- resend_verification mints a new one, which is what invalidates the
        # old link (see test_verify_email_repeat_click_and_supersede for that case and
        # for the same-link-twice case, which is *not* an error). This used to render
        # a raw 404 JSON body in the browser; now it lands on the login page, which
        # says what to do.
        dead = test_client.get("/api/v1/users/verify/dasadsasdadsasdsaddassad", follow_redirects=False)
        assert dead.status_code in (302, 307)
        assert dead.headers["location"] == "/account/login?verified=expired"

        test_client.get(f"/api/v1/users/verify/{user.json()['verify_key']}")
        resp = test_client.post("/api/v1/login/start", json={"email": test_user_email})
        assert resp.status_code == 200
        session_id = resp.json()["session_id"]
        resp = test_client.post(
            f"/api/v1/login/step/1?session_id={session_id}", json={"auth_type": "PASSWORD", "data": test_user_password}
        )
        ValueStorage.cookies = resp.cookies
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_verify_email_repeat_click_and_supersede(self, test_client: TestClient, monkeypatch):  # noqa : F811
        """Clicking the same live confirmation link twice is not an error; a link a
        resend has since replaced is.

        verify_key used to be nulled the moment it verified an account, which made a
        second click on the same link indistinguishable from a dead one -- both landed
        on "verified=expired" with an offer to resend, and resending an already-verified
        address silently does nothing (resend_verification only sends when
        `not user.verified`), so that offer went nowhere. A self-contained user here so
        this doesn't depend on where test_verify_email above leaves the shared one.

        The suite runs with SKIP_EMAIL_VERIFICATION=True, which verifies a new user
        immediately and never mints a verify_key at all -- so this flips that off for
        just this test to exercise the actual confirmation-link path it is testing.
        """
        import frogquiz.routers.users as users_router

        monkeypatch.setattr(users_router.settings, "skip_email_verification", False)

        async def _no_send(**kwargs):
            return None

        monkeypatch.setattr("frogquiz.emails._sendMail", _no_send)
        # byom.de, not example.com: registration runs the real deliverability check
        # (VALIDATE_EMAIL_DELIVERABILITY defaults to True and .env.ci doesn't turn it
        # off), and example.com is the RFC 2606 documentation domain -- genuinely
        # undeliverable, so it 400s. byom.de is the domain every other test that needs
        # a real successful registration already uses (test_user_email, anon_user_email).
        email = f"{uuid.uuid4().hex}@byom.de"
        created = test_client.post(
            "/api/v1/users/create",
            json={"email": email, "password": test_user_password, "username": uuid.uuid4().hex[:12]},
        )
        assert created.status_code == 200
        first_key = test_client.get(
            f"/api/v1/internal/testing/user/{email}?secret_key={settings().secret_key}"
        ).json()["verify_key"]

        # The same link, clicked more than once: every visit after the first still
        # says "verified", not "expired".
        for _ in range(3):
            resp = test_client.get(f"/api/v1/users/verify/{first_key}", follow_redirects=False)
            assert resp.status_code in (302, 307)
            assert resp.headers["location"] == "/account/login?verified=true"
        assert test_client.get(
            f"/api/v1/internal/testing/user/{email}?secret_key={settings().secret_key}"
        ).json()["verified"] is True

        # A second, unverified user whose confirmation mail is replaced by a resend:
        # the old link stops working, the new one verifies.
        email2 = f"{uuid.uuid4().hex}@byom.de"
        created2 = test_client.post(
            "/api/v1/users/create",
            json={"email": email2, "password": test_user_password, "username": uuid.uuid4().hex[:12]},
        )
        assert created2.status_code == 200
        old_key = test_client.get(
            f"/api/v1/internal/testing/user/{email2}?secret_key={settings().secret_key}"
        ).json()["verify_key"]
        resend = test_client.post("/api/v1/users/resend-verification", json={"email": email2})
        assert resend.status_code == 200
        new_key = test_client.get(
            f"/api/v1/internal/testing/user/{email2}?secret_key={settings().secret_key}"
        ).json()["verify_key"]
        assert new_key != old_key

        dead = test_client.get(f"/api/v1/users/verify/{old_key}", follow_redirects=False)
        assert dead.headers["location"] == "/account/login?verified=expired"
        alive = test_client.get(f"/api/v1/users/verify/{new_key}", follow_redirects=False)
        assert alive.headers["location"] == "/account/login?verified=true"

        # TestStats below hardcodes the global user count as 1 (the single
        # test_user_email account), which byom.de made real again -- this test
        # used to register on example.com, which the deliverability check
        # rejected before either row was ever written. Delete both through the
        # real endpoint, the way every other test in this file touches the DB
        # -- calling the ormar model directly from here hit a "different event
        # loop" error, because TestClient runs the ASGI app (and so the DB
        # pool) on its own loop, not this async test function's.
        for cleanup_email in (email, email2):
            login = test_client.post("/api/v1/login/start", json={"email": cleanup_email})
            session_id = login.json()["session_id"]
            step = test_client.post(
                f"/api/v1/login/step/1?session_id={session_id}",
                json={"auth_type": "PASSWORD", "data": test_user_password},
            )
            assert step.status_code == 200
            # test_client.delete() has no json= -- httpx's convenience methods drop
            # the body on DELETE (see test_delete_user_rejects_wrong_password above).
            deleted = test_client.request(
                "DELETE",
                "/api/v1/users/me",
                cookies=step.cookies,
                json={"password": test_user_password},
            )
            assert deleted.status_code == 200

    @pytest.mark.asyncio
    async def test_check(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get("/api/v1/users/check", cookies=ValueStorage.cookies)
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_me(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get("/api/v1/users/me", cookies=ValueStorage.cookies)
        data = resp.json()
        assert resp.status_code == 200
        assert data["verified"] is True
        assert data["email"] == test_user_email
        assert data["username"] == "mawoka"

    # @pytest.mark.asyncio
    # async def test_logout(self, test_client):  # noqa : F811
    #     resp = test_client.get("/api/v1/users/me", cookies={"access_token": access_token})
    #     assert resp.status_code == 200
    #     resp = test_client.get(
    #         "/api/v1/users/logout", cookies={"rememberme_token": rememberme_token}, allow_redirects=False
    #     )
    #     assert resp.status_code == 302
    #     resp = test_client.get("/api/v1/users/me", cookies={"rememberme_token": rememberme_token})
    #     assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_password_update(self, test_client: TestClient):  # noqa : F811
        resp = test_client.put(
            "/api/v1/users/password/update",
            json={"new_password": "new_password", "old_password": test_user_password},
            cookies=ValueStorage.cookies,
        )
        assert resp.status_code == 200
        resp = test_client.put(
            "/api/v1/users/password/update",
            json={"new_password": "asdsdadsasdaasd", "old_password": "asdasdsadadsasdsadasdasd"},
            cookies=ValueStorage.cookies,
        )
        assert resp.status_code == 400
        resp_code = self.log_in(test_client, password="new_password")
        assert resp_code == 200
        resp = test_client.put(
            "/api/v1/users/password/update",
            json={"new_password": test_user_password, "old_password": "new_password"},
            cookies=ValueStorage.cookies,
        )
        assert resp.status_code == 200
        resp_code = self.log_in(test_client)
        assert resp_code == 200
        response = test_client.get("/api/v1/users/me", cookies=ValueStorage.cookies)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_session(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get("/api/v1/users/session", cookies=ValueStorage.cookies)
        assert resp.status_code == 200
        assert resp.json()["ip_address"] == "testclient"

    @pytest.mark.asyncio
    async def test_list_sessions(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get("/api/v1/users/sessions/list", cookies=ValueStorage.cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_delete_session(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get("/api/v1/users/session", cookies=ValueStorage.cookies)
        session_id = resp.json()["id"]
        resp = test_client.delete("/api/v1/users/sessions/" + str(session_id), cookies=ValueStorage.cookies)
        assert resp.status_code == 200
        resp = test_client.delete("/api/v1/users/sessions/asdsadasdasdsad", cookies=ValueStorage.cookies)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_forgotten_password(self, test_client: TestClient, monkeypatch):  # noqa : F811
        # Stub the SMTP send: this route is tested for the reset token it stores, not for
        # delivery. The stub has to be awaitable -- the caller awaits it, and a plain
        # lambda returning None raised inside the handler, which the route then swallowed.
        async def _no_send(**kwargs):
            return None

        monkeypatch.setattr("frogquiz.emails._sendMail", _no_send)
        known = test_client.post("/api/v1/users/forgot-password", json={"email": test_user_email})
        assert known.status_code == 200
        unknown = test_client.post("/api/v1/users/forgot-password", json={"email": "ddassad@dsa.ads"})
        assert unknown.status_code == 200
        # Byte-identical, or the endpoint tells an attacker which addresses are registered.
        assert known.json() == unknown.json()

    @pytest.mark.asyncio
    async def test_resend_verification(self, test_client: TestClient, monkeypatch):  # noqa : F811
        async def _no_send(**kwargs):
            return None

        monkeypatch.setattr("frogquiz.emails._sendMail", _no_send)
        known = test_client.post("/api/v1/users/resend-verification", json={"email": test_user_email})
        assert known.status_code == 200
        unknown = test_client.post("/api/v1/users/resend-verification", json={"email": "nobody@dsa.ads"})
        assert unknown.status_code == 200
        assert known.json() == unknown.json()

    @pytest.mark.asyncio
    async def test_reset_password_rejects_short_password(self, test_client: TestClient):  # noqa : F811
        """The one password-setting route that took no length bound used to take "a"."""
        resp = test_client.post("/api/v1/users/reset-password", json={"token": "whatever", "password": "short"})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_reset_password_with_token(self, test_client: TestClient):  # noqa : F811
        me = test_client.get("/api/v1/users/me", cookies=ValueStorage.cookies).json()
        redis = Redis().from_url(str(settings().redis))
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
        # Following the emailed link proves mailbox control, so the account is verified
        # by it -- otherwise anyone who registered while mail was down stays locked out.
        after = test_client.get(f"/api/v1/internal/testing/user/{test_user_email}?secret_key={settings().secret_key}")
        assert after.json()["verified"] is True
        self.log_in(test_client, password="new_password")
        test_client.put(
            "/api/v1/users/password/update",
            json={"new_password": test_user_password, "old_password": "new_password"},
            cookies=ValueStorage.cookies,
        )
        redis.flushdb()

    @pytest.mark.asyncio
    async def test_signout_everywhere(self, test_client: TestClient):  # noqa : F811
        resp = test_client.delete("/api/v1/users/signout-everywhere", cookies=ValueStorage.cookies)
        assert resp.status_code == 200


class TestUtils:
    @pytest.mark.asyncio
    async def test_get_ip_data(self, test_client: TestClient):  # noqa : F811
        # Off by default (ENABLE_IP_LOOKUP): it has no caller and its provider is HTTP-only.
        # This used to call ip-api.com from CI, so it also only passed while they were up.
        resp = test_client.get("/api/v1/utils/ip-lookup/1.1.1.1", cookies=ValueStorage.cookies)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_qr(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get("/api/v1/utils/qr/12345678")
        assert resp.status_code == 200
        assert resp.headers["Content-Type"] == "image/svg+xml"


class TestStats:
    @pytest.mark.asyncio
    async def test_get_quiz_count(self, test_client: TestClient):  # noqa : F811
        redis = Redis().from_url(str(settings().redis))
        redis.flushdb()
        for _ in range(2):
            resp = test_client.get("/api/v1/stats/quizzes")
            assert resp.status_code == 200
            assert resp.text == str(0)

    @pytest.mark.asyncio
    async def test_get_user_count(self, test_client: TestClient):  # noqa : F811
        redis = Redis().from_url(str(settings().redis))
        redis.flushdb()
        for _ in range(2):
            resp = test_client.get("/api/v1/stats/users")
            assert resp.status_code == 200
            assert resp.text == str(1)

    @pytest.mark.asyncio
    async def test_get_combined_count(self, test_client: TestClient):  # noqa : F811
        redis = Redis().from_url(str(settings().redis))
        redis.flushdb()
        for _ in range(2):
            resp = test_client.get("/api/v1/stats/combined")
            assert resp.status_code == 200
            assert resp.json()["quiz_count"] == 0
            assert resp.json()["user_count"] == 1


class TestQuiz:
    @pytest.mark.asyncio
    async def test_create_quiz(self, test_client: TestClient):  # noqa : F811
        resp = test_client.post("/api/v1/editor/start?edit=false", cookies=ValueStorage.cookies)
        assert resp.status_code == 200
        edit_token = resp.json()["token"]
        assert len(edit_token) == 8
        resp = test_client.post(
            f"/api/v1/editor/finish?edit_id={edit_token}", json=example_quiz, cookies=ValueStorage.cookies
        )
        assert resp.status_code == 200
        resp = test_client.get("/api/v1/quiz/list", cookies=ValueStorage.cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        ValueStorage.quiz_id = data[0]["id"]

    @pytest.mark.asyncio
    async def test_get_quiz_from_id(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get(f"/api/v1/quiz/get/{ValueStorage.quiz_id}", cookies=ValueStorage.cookies)
        assert resp.status_code == 200
        resp = test_client.get("/api/v1/quiz/get/dasdsadsadsadsadsa", cookies=ValueStorage.cookies)
        assert resp.status_code == 400
        resp = test_client.get("/api/v1/quiz/get/847c64d3-39f9-4bb7-8f13-fae913f67858", cookies=ValueStorage.cookies)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_list_quizzes(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get("/api/v1/quiz/list", cookies=ValueStorage.cookies)
        assert resp.status_code == 200
        assert resp.json()[0]["id"] == ValueStorage.quiz_id

    @pytest.mark.asyncio
    async def test_update_quiz(self, test_client: TestClient):  # noqa : F811
        example_quiz["public"] = True
        resp = test_client.post(
            f"/api/v1/editor/start?edit=true&quiz_id={ValueStorage.quiz_id}", cookies=ValueStorage.cookies
        )
        edit_id = resp.json()["token"]
        resp = test_client.post(
            f"/api/v1/editor/finish?edit_id={edit_id}", json=example_quiz, cookies=ValueStorage.cookies
        )
        assert resp.status_code == 200
        resp = test_client.post(
            "/api/v1/editor/start?edit=true&quiz_id=f183e091-a863-44ec-a1b7-c70eb92e3f6a", cookies=ValueStorage.cookies
        )
        assert resp.status_code == 404
        resp = test_client.post("/api/v1/editor/start?edit=true&quiz_id=asddasasdasdads", cookies=ValueStorage.cookies)
        assert resp.status_code == 422
        example_quiz["public"] = False
        resp = test_client.post(
            f"/api/v1/editor/start?edit=true&quiz_id={ValueStorage.quiz_id}", cookies=ValueStorage.cookies
        )
        edit_id = resp.json()["token"]
        test_client.post(f"/api/v1/editor/finish?edit_id={edit_id}", json=example_quiz, cookies=ValueStorage.cookies)
        example_quiz["public"] = True
        resp = test_client.post(
            f"/api/v1/editor/start?edit=true&quiz_id={ValueStorage.quiz_id}", cookies=ValueStorage.cookies
        )
        edit_id = resp.json()["token"]
        test_client.post(f"/api/v1/editor/finish?edit_id={edit_id}", json=example_quiz, cookies=ValueStorage.cookies)

    @pytest.mark.asyncio
    async def test_import_quiz(self, test_client: TestClient):  # noqa : F811
        resp = test_client.post(
            "/api/v1/quiz/import/1f95eb0b-fcf4-4db2-879b-5418ef75116b", cookies=ValueStorage.cookies
        )
        assert resp.status_code == 200
        ValueStorage.imported_quizzes.append(resp.json()["id"])
        resp = test_client.post("/api/v1/quiz/import/1f95eb0bdassdadasdas", cookies=ValueStorage.cookies)
        assert resp.json()["detail"] == "kahoot"

    @pytest.mark.asyncio
    async def test_get_public_quiz(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get(f"/api/v1/quiz/get/public/{ValueStorage.imported_quizzes[0]}")
        assert resp.status_code == 200
        resp = test_client.get(
            "/api/v1/quiz/get/public/f183e091-a863-44ec-a1b7-c70eb92e3f6a", cookies=ValueStorage.cookies
        )
        assert resp.status_code == 404
        resp = test_client.get("/api/v1/quiz/get/public/dadasdas92e3f6a", cookies=ValueStorage.cookies)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_search_get(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get("/api/v1/search/?q=*")
        assert resp.status_code == 200
        assert len(resp.json()["hits"]) > 0

    @pytest.mark.asyncio
    async def test_search_post(self, test_client: TestClient):  # noqa : F811
        resp = test_client.post("/api/v1/search/", json={"q": "*"})
        assert resp.status_code == 200
        assert len(resp.json()["hits"]) > 0

    @pytest.mark.asyncio
    async def test_image_cdn(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get(f"/api/v1/quiz/get/public/{ValueStorage.imported_quizzes[0]}")
        assert resp.status_code == 200
        quiz = resp.json()
        image_id = quiz["questions"][0]["image"]
        # resp = test_client.get(f"/api/v1/storage/download/{image_id}")
        # print(resp.text)
        # assert resp.status_code == 200 This fails because I don't know
        resp = test_client.get(f"/api/v1/storage/download/{image_id}sadgvsadgvhsad")
        assert resp.status_code == 400


class TestPlayQuiz:
    @pytest.mark.asyncio
    async def test_start_quiz(self, test_client: TestClient):  # noqa : F811
        resp = test_client.post(
            "/api/v1/quiz/start/fb5adc91-629e-416e-8b98-ae400e36417c?game_mode=kahoot", cookies=ValueStorage.cookies
        )
        assert resp.status_code == 404
        resp = test_client.post(
            "/api/v1/quiz/start/fb5adc91-629e-416e-8b98-ae400sdadsasadsadasddsae36417c?game_mode=kahoot",
            cookies=ValueStorage.cookies,
        )
        assert resp.status_code == 400
        resp = test_client.post(
            f"/api/v1/quiz/start/{ValueStorage.quiz_id}?game_mode=kahoot", cookies=ValueStorage.cookies
        )
        ValueStorage.game_pin = resp.json()["game_pin"]
        ValueStorage.game_id = resp.json()["game_id"]

    @pytest.mark.asyncio
    async def test_check_captcha_enabled(self, test_client: TestClient):  # noqa : F811
        res = test_client.get(f"/api/v1/quiz/play/check_captcha/{ValueStorage.game_pin}")
        assert res.status_code == 200
        assert res.json()["enabled"] is True

        res = test_client.get("/api/v1/quiz/play/check_captcha/dsadsadas")
        assert res.status_code == 404

    @pytest.mark.asyncio
    async def test_join_game_route(self, test_client: TestClient):  # noqa : F811
        # Retired: it handed the host's game_id to anyone with the PIN.
        res = test_client.get(f"/api/v1/quiz/join/{ValueStorage.game_pin}")
        assert res.status_code == 410
        assert ValueStorage.game_id not in res.text


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
        resp = test_client.get("/api/v1/users/me", cookies=ValueStorage.cookies)
        user = await get_user_from_id(resp.json()["id"])
"""


class TestCommunity:
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, test_client: TestClient):  # noqa : F811
        user = test_client.get("/api/v1/users/me", cookies=ValueStorage.cookies)
        user_id = user.json()["id"]
        resp = test_client.get(f"/api/v1/community/user/{user_id}")
        assert resp.status_code == 200
        resp = test_client.get("/api/v1/community/user/e673c9ca-0cdf-4ebf-bad2-7d009ef5c62b")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_quizzes_from_user(self, test_client: TestClient):  # noqa : F811
        user = test_client.get("/api/v1/users/me", cookies=ValueStorage.cookies)
        user_id = user.json()["id"]
        resp = test_client.get(f"/api/v1/community/quizzes/{user_id}")
        data = resp.json()
        assert type(data) is list


class TestSitemap:
    @pytest.mark.asyncio
    async def test_get_sitemap(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get("/api/v1/sitemap/get")
        assert resp.status_code == 200
        resp = test_client.get("/api/v1/sitemap/get")
        assert resp.status_code == 200


class TestStorage:
    @pytest.mark.asyncio
    async def test_upload_file(self, test_client: TestClient):  # noqa : F811
        # SVG is deliberately absent from ALLOWED_MIME_TYPES (script-injection vector), so upload an allowed type
        resp = test_client.post(
            "/api/v1/storage/", cookies=ValueStorage.cookies, files={"file": ("img.png", b"png_content", "image/png")}
        )
        assert resp.status_code == 200
        data = resp.json()
        ValueStorage.file_id = data["id"]

    @pytest.mark.asyncio
    async def test_upload_raw_file(self, test_client: TestClient):  # noqa : F811
        resp = test_client.request(
            "POST",
            "/api/v1/storage/raw",
            data=b"data!",
            headers={"Content-Type": "image/svg+xml"},
            cookies=ValueStorage.cookies,
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_file_info(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get("/api/v1/storage/meta/dsadsaasdas", cookies=ValueStorage.cookies)
        assert resp.status_code == 422
        resp = test_client.get(
            "/api/v1/storage/meta/35c4f635-906a-46d7-8ab8-0520105ffff5", cookies=ValueStorage.cookies
        )
        assert resp.status_code == 404
        resp = test_client.get(f"/api/v1/storage/meta/{ValueStorage.file_id}", cookies=ValueStorage.cookies)
        data = resp.json()
        assert data["size"] == 0
        assert data["imported"] is False
        assert data["alt_text"] is None
        assert data["filename"] is None
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_update_image_data(self, test_client: TestClient):  # noqa : F811
        resp = test_client.put(
            f"/api/v1/storage/meta/{ValueStorage.file_id}",
            json={"alt_text": "Alt", "filename": "Filename"},
            cookies=ValueStorage.cookies,
        )
        assert resp.status_code == 200
        resp = test_client.put(
            f"/api/v1/storage/meta/{ValueStorage.file_id}",
            json={"alt_text": "", "filename": ""},
            cookies=ValueStorage.cookies,
        )
        assert resp.status_code == 200
        resp = test_client.get(f"/api/v1/storage/meta/{ValueStorage.file_id}", cookies=ValueStorage.cookies)
        data = resp.json()
        assert data["alt_text"] is None
        assert data["filename"] is None

    @pytest.mark.asyncio
    async def test_list_images(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get("/api/v1/storage/list", cookies=ValueStorage.cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert type(data) is list
        assert len(data) >= 2

    @pytest.mark.asyncio
    async def test_get_latest_images(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get("/api/v1/storage/list/last", cookies=ValueStorage.cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert type(data) is list
        assert len(data) >= 2
        resp = test_client.get("/api/v1/storage/list/last?count=1", cookies=ValueStorage.cookies)
        assert resp.status_code == 200
        # assert len(data) == 1

    @pytest.mark.asyncio
    async def test_get_storage_limit(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get("/api/v1/storage/limit", cookies=ValueStorage.cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["limit_reached"] is False
        assert type(data["limit"]) is int
        assert data["used"] == 0


class TestQuizivity:
    @pytest.mark.asyncio
    async def test_create_quiztivity(self, test_client: TestClient):  # noqa : F811
        resp = test_client.post("/api/v1/quiztivity/create", cookies=ValueStorage.cookies, json=example_quiztivity)
        assert resp.status_code == 200
        data = resp.json()
        ValueStorage.quiztivity_id = data["id"]

    @pytest.mark.asyncio
    async def test_get_quiztivity(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get("/api/v1/quiztivity/8bd77201-65ed-46fe-9160-cfe71dad501f", cookies=ValueStorage.cookies)
        assert resp.status_code == 404
        resp = test_client.get(f"/api/v1/quiztivity/{ValueStorage.quiztivity_id}", cookies=ValueStorage.cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == ValueStorage.quiztivity_id

    @pytest.mark.asyncio
    async def test_put_quiztivity(self, test_client: TestClient):  # noqa : F811
        example_quiztivity["title"] = "New title"
        resp = test_client.put(
            f"/api/v1/quiztivity/{ValueStorage.quiztivity_id}", json=example_quiztivity, cookies=ValueStorage.cookies
        )
        assert resp.status_code == 200
        resp = test_client.put(
            "/api/v1/quiztivity/8bd77201-65ed-46fe-9160-cfe71dad501f",
            json=example_quiztivity,
            cookies=ValueStorage.cookies,
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_all_quiztivities(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get("/api/v1/quiztivity/", cookies=ValueStorage.cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert type(data) is list
        assert data[0]["id"] == ValueStorage.quiztivity_id

    @pytest.mark.asyncio
    async def test_create_share(self, test_client: TestClient):  # noqa : F811
        resp = test_client.post(
            "/api/v1/quiztivity/shares/",
            cookies=ValueStorage.cookies,
            json={"quiztivity": ValueStorage.quiztivity_id, "expire_in": None},
        )
        assert resp.status_code == 200
        data = resp.json()
        ValueStorage.share_id = data["id"]
        resp = test_client.post(
            "/api/v1/quiztivity/shares/",
            cookies=ValueStorage.cookies,
            json={"quiztivity": "a090077f-9059-42bc-9783-f2cd01e069b8", "expire_in": None},
        )
        assert resp.status_code == 400
        resp = test_client.post(
            "/api/v1/quiztivity/shares/",
            cookies=ValueStorage.cookies,
            json={"quiztivity": ValueStorage.quiztivity_id, "expire_in": 0},
        )
        data = resp.json()
        ValueStorage.expired_share_id = data["id"]
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_share(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get(
            "/api/v1/quiztivity/shares/8bd77201-65ed-46fe-9160-cfe71dad501f", cookies=ValueStorage.cookies
        )
        assert resp.status_code == 404
        resp = test_client.get(f"/api/v1/quiztivity/shares/{ValueStorage.share_id}", cookies=ValueStorage.cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == ValueStorage.quiztivity_id
        resp = test_client.get(
            f"/api/v1/quiztivity/shares/{ValueStorage.expired_share_id}", cookies=ValueStorage.cookies
        )
        assert resp.status_code == 410

    @pytest.mark.asyncio
    async def test_update_share(self, test_client: TestClient):  # noqa : F811
        resp = test_client.put(
            "/api/v1/quiztivity/shares/8bd77201-65ed-46fe-9160-cfe71dad501f",
            cookies=ValueStorage.cookies,
            json={"expire_in": 50},
        )
        assert resp.status_code == 404
        resp = test_client.put(
            f"/api/v1/quiztivity/shares/{ValueStorage.share_id}", cookies=ValueStorage.cookies, json={"expire_in": 50}
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_share(self, test_client: TestClient):  # noqa : F811
        resp = test_client.delete(
            "/api/v1/quiztivity/shares/8bd77201-65ed-46fe-9160-cfe71dad501f", cookies=ValueStorage.cookies
        )
        assert resp.status_code == 404
        resp = test_client.delete(
            f"/api/v1/quiztivity/shares/{ValueStorage.expired_share_id}", cookies=ValueStorage.cookies
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_shares_by_quiztivity(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get(f"/api/v1/quiztivity/{ValueStorage.quiztivity_id}/shares", cookies=ValueStorage.cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert type(data) is list
        assert data[0]["id"] == ValueStorage.share_id

    @pytest.mark.asyncio
    async def test_get_shares(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get("/api/v1/quiztivity/shares/", cookies=ValueStorage.cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert type(data) is list
        assert data[0]["id"] == ValueStorage.share_id

    @pytest.mark.asyncio
    async def test_delete_quiztivity_requires_auth(self, test_client: TestClient):  # noqa : F811
        # Regression: DELETE /quiztivity/{uuid} carried no auth dependency at all, so
        # anyone who knew a UUID could delete someone else's QuizTivity. The second
        # request proves the object survived the unauthenticated attempt.
        resp = test_client.delete(f"/api/v1/quiztivity/{ValueStorage.quiztivity_id}")
        assert resp.status_code == 401
        resp = test_client.get(
            f"/api/v1/quiztivity/{ValueStorage.quiztivity_id}", cookies=ValueStorage.cookies
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_totp_can_be_switched_off_while_the_flag_is_off(self, test_client: TestClient):  # noqa : F811
        # ENABLE_TOTP is off for the MVP, but the login flow still honours a secret that
        # is already set. If the whole 2fa router were gated, anyone who enabled TOTP
        # before the cut would be stuck behind a factor they cannot remove. Setting it
        # up must 404; reading the status and switching it off must not.
        assert settings().enable_totp is False
        resp = test_client.post(
            "/api/v1/users/2fa/totp",
            json={"password": test_user_password},
            cookies=ValueStorage.cookies,
        )
        assert resp.status_code == 404
        assert (test_client.get("/api/v1/users/2fa/totp", cookies=ValueStorage.cookies)).status_code == 200
        resp = test_client.request(
            "DELETE",
            "/api/v1/users/2fa/totp",
            json={"password": test_user_password},
            cookies=ValueStorage.cookies,
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_quiztivity(self, test_client: TestClient):  # noqa : F811
        test_client.delete(f"/api/v1/quiztivity/shares/{ValueStorage.share_id}", cookies=ValueStorage.cookies)
        resp = test_client.delete(
            "/api/v1/quiztivity/8bd77201-65ed-46fe-9160-cfe71dad501f", cookies=ValueStorage.cookies
        )
        assert resp.status_code == 404
        resp = test_client.delete(f"/api/v1/quiztivity/{ValueStorage.quiztivity_id}", cookies=ValueStorage.cookies)
        assert resp.status_code == 200


class TestAvatar:
    @pytest.mark.asyncio
    async def test_get_customized_avatar(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get("/api/v1/avatar/custom?skin_color=69", cookies=ValueStorage.cookies)
        assert resp.status_code == 400
        resp = test_client.get("/api/v1/avatar/custom", cookies=ValueStorage.cookies)
        assert resp.status_code == 200
        assert "image/svg+xml" in resp.headers.get("Content-Type")

    @pytest.mark.asyncio
    async def test_save_avatar(self, test_client: TestClient):  # noqa : F811
        resp = test_client.post("/api/v1/avatar/save?skin_color=69", cookies=ValueStorage.cookies)
        assert resp.status_code == 400
        resp = test_client.post("/api/v1/avatar/save", cookies=ValueStorage.cookies)
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_own_avatar(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get("/api/v1/users/avatar", cookies=ValueStorage.cookies)
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_other_avatar(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get(
            "/api/v1/users/8bd77201-65ed-46fe-9160-cfe71dad501f/avatar", cookies=ValueStorage.cookies
        )
        assert resp.status_code == 404
        user_id = test_client.get("/api/v1/users/me", cookies=ValueStorage.cookies).json()["id"]
        resp = test_client.get(f"/api/v1/users/avatar/{user_id}", cookies=ValueStorage.cookies)
        assert resp.status_code == 200


class TestExImport:
    @pytest.mark.asyncio
    async def test_export_quiz(self, test_client: TestClient):  # noqa : F811
        resp = test_client.get("/api/v1/eximport/jgfgufgfgfzftzi", cookies=ValueStorage.cookies)
        assert resp.status_code == 422
        resp = test_client.get("/api/v1/eximport/8bd77201-65ed-46fe-9160-cfe71dad501f", cookies=ValueStorage.cookies)
        assert resp.status_code == 404
        resp = test_client.get(f"/api/v1/eximport/{ValueStorage.quiz_id}", cookies=ValueStorage.cookies)
        assert resp.status_code == 200
        exported_data = resp.content
        assert len(exported_data) < 3000
        ValueStorage.exported_quiz_data = exported_data

    @pytest.mark.asyncio
    async def test_import_quiz(self, test_client: TestClient):  # noqa : F811
        resp = test_client.post(
            "/api/v1/eximport/", files={"file": ValueStorage.exported_quiz_data}, cookies=ValueStorage.cookies
        )
        assert resp.status_code == 200


class TestDeleteStuff:
    @pytest.mark.asyncio
    async def test_delete_quiz(self, test_client: TestClient):  # noqa : F811
        resp = test_client.delete(
            f"/api/v1/quiz/delete/{ValueStorage.imported_quizzes[0]}", cookies=ValueStorage.cookies
        )
        assert resp.status_code == 200
        resp = test_client.delete(
            "/api/v1/quiz/delete/be582c77-da03-4271-929c-5d582056eb78", cookies=ValueStorage.cookies
        )
        assert resp.status_code == 404

        resp = test_client.delete(
            "/api/v1/quiz/delete/be582c77-da03-sdaasdadsasddas4271-929c-5d582056eb78", cookies=ValueStorage.cookies
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_delete_user_rejects_wrong_password(self, test_client: TestClient):  # noqa : F811
        # test_client.delete() drops the body -- httpx's convenience methods have no
        # json= for DELETE -- which is why the original version of this test was
        # commented out rather than fixed.
        resp = test_client.request(
            "DELETE",
            "/api/v1/users/me",
            cookies=ValueStorage.cookies,
            json={"password": "not-the-password"},
        )
        assert resp.status_code == 400
        # Still there, and still signed in.
        resp = test_client.get("/api/v1/users/me", cookies=ValueStorage.cookies)
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_user_is_not_blocked_by_a_rating(self, test_client: TestClient):  # noqa : F811
        """The account being deleted has rated its own public quiz.

        `rating.user` and `rating.quiz` had no ON DELETE action, so this row blocked
        the delete halfway: the quiz delete failed on rating.quiz, or the user delete
        failed on rating.user one step later -- after the sessions and every quiz were
        already gone and committed. Without this seeded row the test passes on the
        broken code and proves nothing. See migration c3f8a1d47b62.
        """
        resp = test_client.post(
            f"/api/v1/community/rate/{ValueStorage.quiz_id}",
            cookies=ValueStorage.cookies,
            json={"type": "LIKE"},
        )
        assert resp.status_code == 200, "the seed this test depends on did not happen"

        resp = test_client.request(
            "DELETE",
            "/api/v1/users/me",
            cookies=ValueStorage.cookies,
            json={"password": test_user_password},
        )
        assert resp.status_code == 200
        # The cookie has to be cleared by the server: it is httponly, so the page
        # cannot drop it, and hooks.server.ts would keep reporting the user as signed
        # in on the next request.
        assert "access_token" in resp.headers.get("set-cookie", "")

    @pytest.mark.asyncio
    async def test_deleted_user_session_stops_working(self, test_client: TestClient):  # noqa : F811
        """get_current_user resolves out of Redis, and this request's own auth warmed
        that entry, so without clear_cache_for_account a deleted account kept
        authenticating for the full cache_expiry (24h)."""
        resp = test_client.get("/api/v1/users/me", cookies=ValueStorage.cookies)
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_can_register_again_after_delete(self, test_client: TestClient):  # noqa : F811
        """The cleanest proof the row actually went: re-registering the same address
        returns 200 rather than the 409 a surviving account would give."""
        resp = test_client.post(
            "/api/v1/users/create",
            json={"email": test_user_email, "password": test_user_password, "username": "mawoka"},
        )
        assert resp.status_code == 200


def test_check_question_scoring_is_all_or_nothing():
    """A multiple-answer question is scored whole: the indices the player ticked must
    match the indices marked right exactly. See docs/mvp-scope.md."""
    answers = [
        ABCDQuizAnswer(right=True, answer="a"),
        ABCDQuizAnswer(right=False, answer="b"),
        ABCDQuizAnswer(right=True, answer="c"),
        ABCDQuizAnswer(right=False, answer="d"),
    ]
    assert check_check_question("02", answers) is True
    # One of the two right answers, but not both.
    assert check_check_question("0", answers) is False
    # Both right answers plus a wrong one.
    assert check_check_question("023", answers) is False
    # Everything ticked.
    assert check_check_question("0123", answers) is False
    # Nothing ticked.
    assert check_check_question("", answers) is False
