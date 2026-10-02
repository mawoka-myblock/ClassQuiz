# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0


import logging
import gzip
import os

import asyncpg.exceptions
from datetime import datetime

import ormar
import pydantic
from email_validator import validate_email, EmailNotValidError
from fastapi import APIRouter, Response, HTTPException, Request, Depends
from fastapi.responses import JSONResponse, RedirectResponse


from frogquiz import oauth
from frogquiz.helpers.avatar import gzipped_user_avatar
import base64

from frogquiz.auth import (
    get_password_hash,
    hash_session_key,
    revoke_token,
    verify_password,
    get_current_user,
)
from frogquiz.cache import clear_cache_for_account
from frogquiz.config import redis, settings, meilisearch, storage
from frogquiz.helpers.ratelimit import rate_limit, rate_limit_key
import uuid
import bleach
from pydantic import BaseModel
from frogquiz.db import database
from frogquiz.db.models import User, UserSession, UpdatePassword, Quiz, ApiKey, StorageItem
from frogquiz.emails import send_register_email, send_forgotten_password_email
from frogquiz.routers.users import webauthn, twofa

settings = settings()
LOGGER = logging.getLogger("frogquiz.users")

router = APIRouter()

router.include_router(webauthn.router, prefix="/webauthn")
# Mounted whatever ENABLE_TOTP says. The flag is applied per endpoint inside the
# router: setting TOTP up 404s when it is off, but reading the status and switching
# it off do not, so nobody who enabled it before the cut is stranded behind a factor
# they can no longer remove. See docs/mvp-scope.md.
router.include_router(twofa.router, prefix="/2fa")


class RouteUser(pydantic.BaseModel):
    username: str
    # Mirrors the rule the register form enforces; without it the API accepted
    # a one-character password.
    password: str = pydantic.Field(min_length=8, max_length=100)
    email: str


async def find_user_by_email(email: str) -> User | None:
    """Look an account up by address, case-insensitively.

    Addresses are stored folded (see create_user), so the folded lookup is the
    one that matters. The second query is for rows written before that rule
    existed: without it, someone who registered as "Foo@bar.com" silently gets
    no reset email and no way to find out why, because every response on that
    path is deliberately identical.
    """
    folded = email.strip().lower()
    user = await User.objects.filter(email=folded).get_or_none()
    if user is None and folded != email:
        user = await User.objects.filter(email=email).get_or_none()
    return user


async def _sign_out_everywhere(user: User) -> None:
    await UserSession.objects.filter(user=user).delete()
    await clear_cache_for_account(user)


router.include_router(oauth.router, tags=["users", "oauth"], prefix="/oauth")


@router.post(
    "/create",
    response_model=User,
    response_model_include={"id": ..., "verified": ..., "email": ...},
)
async def create_user(user: RouteUser, request: Request) -> User | JSONResponse:
    await rate_limit(request, "register", limit=10, window_seconds=3600)
    if settings.registration_disabled:
        raise HTTPException(status_code=423)
    # Checked before anything is written. Without it the row is created, the send
    # fails, and the rollback below is the only thing standing between the caller
    # and an account they can never verify.
    if not settings.skip_email_verification and not settings.mail_configured:
        raise HTTPException(
            status_code=503,
            detail="This server requires email verification but has no mail server configured.",
        )
    user: User = User(
        **user.model_dump(),
        id=uuid.uuid4(),
        avatar=gzipped_user_avatar(),
        created_at=datetime.now(),
    )
    try:
        # Deliverability is a live DNS/MX lookup, so it needs outbound DNS at signup
        # and rejects internal-only mail domains. On by default; see the setting.
        validated = validate_email(user.email, check_deliverability=settings.validate_email_deliverability)
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # Store one canonical form. The validator folds the domain; the local part is
    # folded here too, because every mail provider treats it case-insensitively and
    # the alternative is two accounts on what the owner considers one address --
    # with only one of them reachable by the reset and resend lookups.
    user.email = validated.normalized.strip().lower()
    # Keyed on the canonical address, so it survives casing tricks and, unlike the
    # per-IP bucket above, cannot be reset by forging a header or moving address.
    # This is what stops one inbox being flooded with confirmation mail from many
    # source addresses.
    await rate_limit_key(f"register_addr:{user.email}", limit=5, window_seconds=3600)
    user.verify_key = str(os.urandom(16).hex())
    res = await User.objects.filter((User.email == user.email) | (User.username == user.username)).all()
    if len(res) != 0:
        raise HTTPException(status_code=409, detail="User already exists")

    user.password = get_password_hash(user.password)
    user.username = bleach.clean(user.username, tags=[], strip=True)
    if len(user.username) == 32:
        return JSONResponse({"details": "Username mustn't be 32 characters long"}, 400)
    try:
        await user.save()
    except asyncpg.exceptions.UniqueViolationError:
        # The check above is not atomic with the insert. Two submissions of the same
        # form -- a double click, a retried request -- raced through it and the loser
        # got a 500 rather than the 409 the first duplicate got.
        raise HTTPException(status_code=409, detail="User already exists")
    if settings.skip_email_verification:
        user.verify_key = None
        user.verified = True
        await user.update()
    else:
        try:
            await send_register_email(user)
        except Exception:
            # The row was already committed, so a failing mail server used to leave
            # an unverified account behind and 500 the request. The caller then saw a
            # generic error, retried, and got 409 "user already exists" forever --
            # locked out of an address they could never verify, with no resend
            # endpoint to recover through. Undo the save so retrying actually works.
            LOGGER.exception("Could not send the verification email to a new user; rolling back")
            await user.delete()
            raise HTTPException(
                status_code=502,
                detail="Could not send the verification email. Nothing was saved -- please try again.",
            )
    await redis.delete("global_user_count")
    return user


@router.get("/logout")
async def logout(request: Request, response: Response):
    remember_token = request.cookies.get("rememberme_token")
    if remember_token is not None:
        await UserSession.objects.filter(session_key=hash_session_key(remember_token)).delete()
    # Clearing the cookie only affects this browser; dropping the Redis entry is
    # what actually ends the session for a token that has already been copied.
    access_token = request.cookies.get("access_token")
    if access_token is not None:
        await revoke_token(access_token.removeprefix("Bearer "))
    response.delete_cookie("access_token")
    response.delete_cookie("expiry")
    response.delete_cookie("rememberme")
    response.delete_cookie("rememberme_token")
    response.status_code = 302
    response.headers["Location"] = "/"
    return response


@router.get("/check")
async def check_token(user: User = Depends(get_current_user)):
    return {"email": user.email}


@router.get("/verify/{verify_key}")
async def verify_user(verify_key: str, request: Request):
    # The key is 128 bits of os.urandom, so this is not guessable and the limit is
    # defence in depth -- it keeps an unauthenticated endpoint from being used to
    # hammer the database. Generous, because a real person may click the same link
    # a few times.
    await rate_limit(request, "verify_email", limit=30, window_seconds=3600)
    user = await User.objects.filter(verify_key=verify_key).get_or_none()
    if user is None:
        # A wrong or superseded key -- asking for a new confirmation mail mints a
        # fresh one, which is what makes the old one stop resolving here. Send them
        # to the login page, which says what to do next, rather than to a dead end.
        return RedirectResponse(url="/account/login?verified=expired")
    # Deliberately NOT clearing verify_key on success. The commonest way back to
    # this same URL is clicking the same link twice -- a double click, a mail
    # client that pre-fetches links, opening the confirmation mail again days
    # later -- and nulling the key made every one of those look identical to a
    # dead link: "verified=expired" with an offer to resend, which silently does
    # nothing because resend_verification only sends when `not user.verified`.
    # An already-verified account is told to log in, not sent looking for a mail
    # that was never going to arrive. The key still dies the moment a *new* one is
    # minted (resend_verification overwrites this column), which is the other
    # thing "expired" needs to mean -- the older of two mails.
    if not user.verified:
        user.verified = True
        await user.update()
        # The cached copy still says unverified otherwise, for a full cache_expiry.
        await clear_cache_for_account(user)
    return RedirectResponse(url="/account/login?verified=true")


@router.put("/password/update")
async def change_password(
    password_data: UpdatePassword,
    response: Response,
    user: User = Depends(get_current_user),
):
    # Same reasoning as DELETE /me: this checks a password, each check is a
    # deliberately expensive argon2 verify, and the account is the thing under
    # attack -- so the bucket is the account, which a caller cannot forge.
    # Consumed on every attempt, not only failed ones, which is the simple version
    # and means a run of typos counts against the limit. Ten an hour is chosen to be
    # well clear of that: somebody mistyping their current password a few times in a
    # row should never meet it, and a session-stealer grinding at the password still
    # meets it quickly.
    await rate_limit_key(f"password_update:{user.id}", limit=10, window_seconds=3600)
    if user.password is None:
        raise HTTPException(status_code=400, detail="This account has no password to change")
    if not verify_password(password_data.old_password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    user.password = get_password_hash(password_data.new_password)
    await user.update()
    await clear_cache_for_account(user)
    await UserSession.objects.filter(user=user).delete()
    response.delete_cookie("access_token")
    response.delete_cookie("expiry")
    response.delete_cookie("rememberme")
    response.delete_cookie("rememberme_token")
    return {"message": "Password updated successfully"}


@router.delete("/signout-everywhere")
async def signout_everywhere(response: Response, user: User = Depends(get_current_user)):
    await _sign_out_everywhere(user)
    response.delete_cookie("access_token")
    response.delete_cookie("expiry")
    response.delete_cookie("rememberme")
    response.delete_cookie("rememberme_token")
    return {"message": "Signout everywhere"}


@router.get(
    "/me",
    response_model_exclude={
        "password",
        "verify_key",
        "usersessions",
        "avatar",
        "quizs",
        "fidocredentialss",
        "backup_code",
        "apikeys",
        "totp_secret",
    },
    response_model=User,
)
async def get_me(user: User = Depends(get_current_user)):
    return user


class ForgotPassword(BaseModel):
    email: str


# Deliberately identical for every outcome: address on file or not, mail sent or
# not. Anything else turns this endpoint into a way to test whether an address has
# an account here.
_RESET_ACK = {"message": "If that address has an account, a reset link is on its way."}


@router.post("/forgot-password")
async def forgotten_password(forgot_password: ForgotPassword, request: Request):
    # Unrated, this endpoint can be used to spam a victim's inbox or hammer the DB.
    await rate_limit(request, "forgot_password", limit=5, window_seconds=3600)
    if not settings.mail_configured:
        raise HTTPException(status_code=503, detail="This server has no mail server configured.")
    # Limited per address as well as per source IP. The IP bucket is what stops
    # someone walking a list of addresses; this is what stops one mailbox being
    # flooded from a spread of addresses, and it keeps working behind a proxy that
    # collapses every caller onto one source IP. Applied before the lookup, so a
    # 429 says nothing about whether the address is on file.
    await rate_limit_key(f"forgot_password_addr:{forgot_password.email.strip().lower()}", limit=3, window_seconds=3600)
    # Unverified accounts used to be excluded, which left anyone who registered
    # while mail was down with no way back in at all -- they could not verify and
    # could not reset. Clicking the link proves control of the mailbox either way,
    # so reset_password_with_token marks them verified when they do.
    user = await find_user_by_email(forgot_password.email)
    if user is not None:
        try:
            await send_forgotten_password_email(user)
        except Exception:
            # A 500 here answers the question the neutral message is there to
            # avoid: only a real address can reach the code that fails.
            LOGGER.exception("Could not send a password reset email")
    return _RESET_ACK


class ResendVerification(BaseModel):
    email: str


@router.post("/resend-verification")
async def resend_verification(body: ResendVerification, request: Request):
    """Send the confirmation mail again.

    Registration had no recovery path: if the first mail was lost, filtered, or
    sent while the relay was down, the address stayed unverified and re-registering
    returned 409 forever.
    """
    await rate_limit(request, "resend_verification", limit=5, window_seconds=3600)
    if not settings.mail_configured:
        raise HTTPException(status_code=503, detail="This server has no mail server configured.")
    await rate_limit_key(f"resend_verification_addr:{body.email.strip().lower()}", limit=3, window_seconds=3600)
    user = await find_user_by_email(body.email)
    if user is not None and not user.verified:
        # The old key may be in a mail the user cannot find. Minting a new one
        # keeps exactly one link live per address.
        user.verify_key = str(os.urandom(16).hex())
        await user.update()
        try:
            await send_register_email(user)
        except Exception:
            LOGGER.exception("Could not resend a verification email")
    return {"message": "If that address needs confirming, a new link is on its way."}


class ResetPassword(BaseModel):
    # Registration and the change-password route both bound this; reset did not, so
    # the one flow reachable without knowing the old password was also the one that
    # accepted a one-character replacement.
    password: str = pydantic.Field(min_length=8, max_length=100)
    token: str


@router.post("/reset-password")
async def reset_password_with_token(reset_password: ResetPassword, response: Response):
    # GETDEL rather than GET-then-DELETE, so two concurrent requests for the same
    # token can't both pass the check before either invalidates it.
    redis_res = await redis.getdel(f"reset_passwd:{reset_password.token}")
    if redis_res is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = await User.objects.filter(id=uuid.UUID(redis_res)).get_or_none()
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    user.password = get_password_hash(reset_password.password)
    # Following the link is proof of mailbox control, which is all verification
    # ever asserted -- so an account that reset this way is verified by definition.
    user.verified = True
    user.verify_key = None
    await user.update()
    # The token is already gone (GETDEL above); drop the pointer that tracks which
    # one is current, so the next request does not try to revoke a spent token.
    await redis.delete(f"reset_passwd_current:{user.id}")
    await _sign_out_everywhere(user)
    response.delete_cookie("access_token")
    response.delete_cookie("expiry")
    response.delete_cookie("rememberme")
    response.delete_cookie("rememberme_token")
    return {"message": "Password updated successfully"}


@router.get(
    "/sessions/list",
    response_model=list[UserSession],
    response_model_exclude={"user", "session_key", "quizs"},
)
async def list_sessions(user: User = Depends(get_current_user)):
    sessions = await UserSession.objects.filter(user=user).all()
    return [session.model_dump() for session in sessions]


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: uuid.UUID, user: User = Depends(get_current_user)):
    await UserSession.objects.filter(user=user, id=session_id).delete()
    return {"message": "Session deleted"}


@router.get(
    "/session",
    response_model=UserSession,
    response_model_exclude={"user": ..., "session_key": ..., "quizs": ...},
)
async def get_session(request: Request, user: User = Depends(get_current_user)):
    try:
        session = await UserSession.objects.filter(
            user=user, session_key=hash_session_key(request.cookies.get("rememberme_token") or "")
        ).first()
        return session
    except ormar.NoMatch:
        raise HTTPException(status_code=404, detail="Session not found")


class DeleteUserInput(BaseModel):
    password: str


@router.delete("/me")
async def delete_user_account(
    input_data: DeleteUserInput,
    request: Request,
    response: Response,
    user: User = Depends(get_current_user),
):
    # Keyed on the account, not the source address: the caller is already
    # authenticated, so the account is the thing being attacked, and each attempt
    # costs a deliberately expensive argon2 verify. Unthrottled, this is both a
    # password oracle behind a borrowed session and a cheap way to burn CPU.
    await rate_limit_key(f"delete_account:{user.id}", limit=5, window_seconds=3600)
    # OAuth accounts are created with no password at all (frogquiz/oauth/*), and
    # verify_password(x, None) raises rather than returning False -- a 500 with no
    # explanation for the one person who cannot act on it.
    if user.password is None:
        raise HTTPException(status_code=400, detail="This account has no password to confirm with")
    if not verify_password(input_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    # Everything the cleanup needs, read before anything is destroyed.
    #
    # Deliberately NOT re-reading the user from the database first. get_current_user
    # resolves through the Redis cache, so a double submit authenticates a user whose
    # row is already gone; the old code re-read into a local that was then None, and
    # `filter(user_id=None)` is not "no quizzes", it is every anonymous quiz in the
    # database. The cached instance carries id, email and username, which is all of
    # what is used below.
    public_quiz_ids = [str(quiz.id) for quiz in await Quiz.objects.filter(user_id=user, public=True).all()]
    storage_names = [
        item.storage_path or item.id.hex for item in await StorageItem.objects.filter(user=user, deleted_at=None).all()
    ]
    api_keys = [row.key for row in await ApiKey.objects.filter(user=user).all()]

    # One commit or none. A failure partway through used to leave an account signed
    # out everywhere with every quiz deleted and the account itself still present --
    # the worst of the available outcomes, and the likely one before the rating and
    # controller foreign keys were made to cascade (c3f8a1d47b62).
    async with database.transaction():
        await UserSession.objects.filter(user=user).delete()
        await Quiz.objects.filter(user_id=user).delete()
        await User.objects.filter(id=user.id).delete()

    # Past this point the account is gone, so nothing below is allowed to fail the
    # request -- a raised exception here would report failure for work that is
    # already committed and cannot be undone.
    #
    # The cache clear is the load-bearing one: get_current_user reads the user out of
    # Redis, where this very request just warmed an entry, so without it a deleted
    # account keeps authenticating for up to cache_expiry (24h).
    # Cookies first, because setting them on the response cannot fail. Redis can,
    # and if it did before this point the browser would still be holding a session
    # for an account that no longer exists.
    response.delete_cookie("access_token")
    response.delete_cookie("expiry")
    response.delete_cookie("rememberme")
    response.delete_cookie("rememberme_token")
    try:
        await clear_cache_for_account(user)
        access_token = request.cookies.get("access_token")
        if access_token is not None:
            await revoke_token(access_token.removeprefix("Bearer "))
        for key in api_keys:
            await redis.delete(f"apikey:{key}")
    except Exception:
        # Worth a loud log: until the entry expires, the deleted account's token
        # still resolves to a cached user. Raising here would report failure for a
        # deletion that has already committed, which is worse.
        LOGGER.exception("Deleted a user but could not clear their Redis session state")

    # Both of these are best-effort, and both run after the commit on purpose.
    # Meilisearch used to be stripped *before* a delete that could fail, which left
    # quizzes in the database and missing from search. This way round the residue of
    # an outage is stale documents, which the reindex job repairs.
    if public_quiz_ids:
        try:
            meilisearch.index(settings.meilisearch_index).delete_documents(public_quiz_ids)
        except Exception:
            LOGGER.exception("Could not remove a deleted user's quizzes from the search index")
    # storage_items is ON DELETE SET NULL, so the rows survive with no owner and the
    # bytes outlive the account unless they are removed here. The privacy policy says
    # deleting an account takes uploads with it; this is what makes that true.
    if storage_names:
        try:
            await storage.delete(storage_names)
        except Exception:
            LOGGER.exception("Could not delete a deleted user's uploads")

    return {"message": "Account deleted"}


@router.get("/avatar")
async def get_own_avatar(user: User = Depends(get_current_user)):
    # See routers/avatar.py: a patched Content-Type left text/plain in place as a
    # second header and every avatar rendered as a broken image.
    return Response(content=gzip.decompress(base64.b64decode(user.avatar)), media_type="image/svg+xml")


@router.get("/avatar/{user_id}")
async def get_other_avatar(user_id: uuid.UUID):
    user = await User.objects.filter(id=user_id).get_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(content=gzip.decompress(base64.b64decode(user.avatar)), media_type="image/svg+xml")


class InternalAuthData(BaseModel):
    rememberme: str
    jwt: str | None = None


class GetEmailFromJWT(BaseModel):
    jwt: str


@router.post("/api_keys", response_model=ApiKey, response_model_include={"key"})
async def generate_api_key(user: User = Depends(get_current_user)):
    key = ApiKey(key=os.urandom(24).hex(), user=user)
    await key.save()
    return key.model_dump(include={"key"})


@router.get("/api_keys", response_model=list[ApiKey], response_model_include={"key"})
async def list_api_keys(user: User = Depends(get_current_user)):
    keys = await ApiKey.objects.filter(user=user).all()
    return keys


@router.delete("/api_keys")
async def delete_api_key(api_key: str, user: User = Depends(get_current_user)):
    key = await ApiKey.objects.get_or_none(key=api_key, user=user)
    if key is None:
        raise HTTPException(status_code=404, detail="Key not found")
    await redis.delete(f"apikey:{key.key}")
    await key.delete()
