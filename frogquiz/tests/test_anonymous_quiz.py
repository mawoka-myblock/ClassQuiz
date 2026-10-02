# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0

"""Anonymous (accountless) quiz creation, hosting, and claiming.

A quiz created without logging in proves ownership with a secret minted at
creation instead of a JWT. These tests exercise that secret end to end: an
anonymous caller can create/edit/host their own quiz, no one else can with a
wrong or missing secret, and a signed-in user can later claim it onto their
account -- after which the secret stops working and the quiz behaves like any
other account-owned one.
"""

import copy

import pytest
from fastapi.testclient import TestClient

from frogquiz.config import settings
from frogquiz.tests import test_client, example_quiz  # noqa: F401

# This suite creates a verified user and a quiz, while test_server.py's
# TestStats asserts the exact global user and quiz counts. Running last means
# those counts are taken before these rows exist, and test_cleanup_claimer_user
# below removes them again afterwards.
pytestmark = pytest.mark.order(-1)

anon_user_email = "anon-quiz-claimer@byom.de"
anon_user_password = "test-password"


class AnonState:
    quiz_id = None
    secret = None
    claimer_cookies = None


class TestAnonymousQuiz:
    @pytest.mark.asyncio
    async def test_create_anonymous_quiz(self, test_client: TestClient):  # noqa: F811
        resp = test_client.post("/api/v1/editor/start?edit=false")
        assert resp.status_code == 200
        edit_token = resp.json()["token"]

        quiz_input = copy.deepcopy(example_quiz)
        quiz_input["public"] = True  # anonymous quizzes must be forced private anyway
        resp = test_client.post(f"/api/v1/editor/finish?edit_id={edit_token}", json=quiz_input)
        assert resp.status_code == 200
        secret = resp.headers.get("X-Anon-Secret")
        assert secret is not None
        AnonState.secret = secret
        AnonState.quiz_id = resp.json()["id"]

    @pytest.mark.asyncio
    async def test_anonymous_quiz_is_never_public(self, test_client: TestClient):  # noqa: F811
        resp = test_client.get(f"/api/v1/quiz/get/public/{AnonState.quiz_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["public"] is False
        # No owner to show, and the response must not crash resolving one.
        assert data["user_id"] is None
        # The ownership hash must not ride along on an unauthenticated response.
        assert "anon_secret" not in data
        # The expiry does, though -- the view page shows the holder when it goes.
        assert data["expire_at"] is not None

    @pytest.mark.asyncio
    async def test_edit_anonymous_quiz_requires_correct_secret(self, test_client: TestClient):  # noqa: F811
        resp = test_client.post(f"/api/v1/editor/start?edit=true&quiz_id={AnonState.quiz_id}")
        assert resp.status_code == 404  # no secret at all

        resp = test_client.post(
            f"/api/v1/editor/start?edit=true&quiz_id={AnonState.quiz_id}",
            headers={"X-Anon-Secret": "not-the-right-secret"},
        )
        assert resp.status_code == 404

        resp = test_client.post(
            f"/api/v1/editor/start?edit=true&quiz_id={AnonState.quiz_id}",
            headers={"X-Anon-Secret": AnonState.secret},
        )
        assert resp.status_code == 200
        edit_id = resp.json()["token"]
        resp = test_client.post(
            f"/api/v1/editor/finish?edit_id={edit_id}",
            json=example_quiz,
            headers={"X-Anon-Secret": AnonState.secret},
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_start_anonymous_quiz_requires_correct_secret(self, test_client: TestClient):  # noqa: F811
        resp = test_client.post(f"/api/v1/quiz/start/{AnonState.quiz_id}?game_mode=kahoot")
        assert resp.status_code == 404

        resp = test_client.post(
            f"/api/v1/quiz/start/{AnonState.quiz_id}?game_mode=kahoot",
            headers={"X-Anon-Secret": "wrong"},
        )
        assert resp.status_code == 404

        resp = test_client.post(
            f"/api/v1/quiz/start/{AnonState.quiz_id}?game_mode=kahoot",
            headers={"X-Anon-Secret": AnonState.secret},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["game_pin"] is not None
        assert data["user_id"] is None

    @pytest.mark.asyncio
    async def test_delete_anonymous_quiz_requires_correct_secret(self, test_client: TestClient):  # noqa: F811
        """The anonymous creator's way out.

        Delete used to require a login, so a quiz made without an account could
        be edited and hosted by its creator but never removed by them -- the
        only way back was waiting for the 30-day sweep.
        """
        # A throwaway quiz, so this does not disturb the claim flow below.
        resp = test_client.post("/api/v1/editor/start?edit=false")
        edit_token = resp.json()["token"]
        resp = test_client.post(f"/api/v1/editor/finish?edit_id={edit_token}", json=example_quiz)
        assert resp.status_code == 200
        throwaway_id = resp.json()["id"]
        throwaway_secret = resp.headers["X-Anon-Secret"]

        resp = test_client.delete(f"/api/v1/quiz/delete/{throwaway_id}")
        assert resp.status_code == 404  # no secret at all

        resp = test_client.delete(
            f"/api/v1/quiz/delete/{throwaway_id}", headers={"X-Anon-Secret": "not-the-right-secret"}
        )
        assert resp.status_code == 404

        # Still there after both refusals.
        assert test_client.get(f"/api/v1/quiz/get/public/{throwaway_id}").status_code == 200

        resp = test_client.delete(f"/api/v1/quiz/delete/{throwaway_id}", headers={"X-Anon-Secret": throwaway_secret})
        assert resp.status_code == 200
        assert test_client.get(f"/api/v1/quiz/get/public/{throwaway_id}").status_code == 404

        # And the secret does not work twice.
        resp = test_client.delete(f"/api/v1/quiz/delete/{throwaway_id}", headers={"X-Anon-Secret": throwaway_secret})
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_claim_requires_login(self, test_client: TestClient):  # noqa: F811
        resp = test_client.post(f"/api/v1/quiz/claim/{AnonState.quiz_id}", headers={"X-Anon-Secret": AnonState.secret})
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_claim_setup_user(self, test_client: TestClient):  # noqa: F811
        resp = test_client.post(
            "/api/v1/users/create",
            json={"email": anon_user_email, "password": anon_user_password, "username": "anon-claimer"},
        )
        assert resp.status_code == 200
        user = test_client.get(f"/api/v1/internal/testing/user/{anon_user_email}?secret_key={settings().secret_key}")
        test_client.get(f"/api/v1/users/verify/{user.json()['verify_key']}")
        resp = test_client.post("/api/v1/login/start", json={"email": anon_user_email})
        session_id = resp.json()["session_id"]
        resp = test_client.post(
            f"/api/v1/login/step/1?session_id={session_id}",
            json={"auth_type": "PASSWORD", "data": anon_user_password},
        )
        assert resp.status_code == 200
        AnonState.claimer_cookies = resp.cookies

    @pytest.mark.asyncio
    async def test_claim_wrong_secret(self, test_client: TestClient):  # noqa: F811
        resp = test_client.post(
            f"/api/v1/quiz/claim/{AnonState.quiz_id}",
            headers={"X-Anon-Secret": "wrong"},
            cookies=AnonState.claimer_cookies,
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_claim_success(self, test_client: TestClient):  # noqa: F811
        resp = test_client.post(
            f"/api/v1/quiz/claim/{AnonState.quiz_id}",
            headers={"X-Anon-Secret": AnonState.secret},
            cookies=AnonState.claimer_cookies,
        )
        assert resp.status_code == 200
        assert resp.json()["user_id"] is not None  # now set, and serializing an owner doesn't crash

        resp = test_client.get("/api/v1/quiz/list", cookies=AnonState.claimer_cookies)
        assert resp.status_code == 200
        assert any(q["id"] == AnonState.quiz_id for q in resp.json())

    @pytest.mark.asyncio
    async def test_claimed_quiz_no_longer_usable_with_old_secret(self, test_client: TestClient):  # noqa: F811
        resp = test_client.post(
            f"/api/v1/editor/start?edit=true&quiz_id={AnonState.quiz_id}",
            headers={"X-Anon-Secret": AnonState.secret},
        )
        assert resp.status_code == 404

        resp = test_client.post(
            f"/api/v1/quiz/claim/{AnonState.quiz_id}",
            headers={"X-Anon-Secret": AnonState.secret},
            cookies=AnonState.claimer_cookies,
        )
        assert resp.status_code == 404

        # The important one: once a quiz has an owner, the anonymous delete path
        # must not reach it. Otherwise a stale secret would be a way to destroy
        # data inside someone's account.
        resp = test_client.delete(
            f"/api/v1/quiz/delete/{AnonState.quiz_id}", headers={"X-Anon-Secret": AnonState.secret}
        )
        assert resp.status_code == 404
        assert test_client.get("/api/v1/quiz/list", cookies=AnonState.claimer_cookies).status_code == 200
        assert any(
            q["id"] == AnonState.quiz_id
            for q in test_client.get("/api/v1/quiz/list", cookies=AnonState.claimer_cookies).json()
        )

    @pytest.mark.asyncio
    async def test_cleanup_claimer_user(self, test_client: TestClient):  # noqa: F811
        # This suite's user (and, via cascade, the claimed quiz) must not
        # survive it -- test_server.py's stats tests assert exact user/quiz
        # counts, which a leftover row here would throw off.
        resp = test_client.request(
            "DELETE",
            "/api/v1/users/me",
            json={"password": anon_user_password},
            cookies=AnonState.claimer_cookies,
        )
        assert resp.status_code == 200
