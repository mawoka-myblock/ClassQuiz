# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import uuid

import asyncpg
import authlib.integrations.base_client
from fastapi import APIRouter, Request, HTTPException, Response

from classquiz.auth import check_token
from classquiz.config import settings
from fastapi.responses import RedirectResponse
from classquiz.db.models import User, UserAuthTypes
from pydantic import BaseModel
from classquiz.helpers.avatar import gzipped_user_avatar
from classquiz.oauth.authenticate_user import log_user_in, rememberme_check
from datetime import datetime
from classquiz.oauth.init_oauth import init_oauth

settings = settings()

router = APIRouter()


class Plan(BaseModel):
    name: str
    space: int
    collaborators: int
    private_repos: int


class GitHubOauthResponse(BaseModel):
    login: str
    id: int
    email: str | None = None
    node_id: str | None = None
    avatar_url: str | None = None
    gravatar_id: str | None = None
    url: str | None = None
    html_url: str | None = None
    followers_url: str | None = None
    following_url: str | None = None
    gists_url: str | None = None
    starred_url: str | None = None
    subscriptions_url: str | None = None
    organizations_url: str | None = None
    repos_url: str | None = None
    events_url: str | None = None
    received_events_url: str | None = None
    type: str | None = None
    site_admin: bool | None = None
    name: str | None = None
    company: str | None = None
    blog: str | None = None
    location: str | None = None
    hireable: bool | None = None
    bio: str | None = None
    twitter_username: str | None = None
    public_repos: int | None = None
    public_gists: int | None = None
    followers: int | None = None
    following: int | None = None
    created_at: datetime
    updated_at: datetime
    private_gists: int | None = None
    total_private_repos: int | None = None
    owned_private_repos: int | None = None
    disk_usage: int | None = None
    collaborators: int | None = None
    two_factor_authentication: bool | None = None
    plan: Plan | None = None


@router.get("/login")
async def github_login(req: Request):
    if settings.github_client_id is None or settings.github_client_secret is None:
        raise HTTPException(status_code=501, detail="GitHub-Login isn't available on this server")
    oauth = init_oauth()
    return await oauth.github.authorize_redirect(req, f"{settings.root_address}/api/v1/users/oauth/github/auth")


@router.get("/auth")
async def auth(request: Request, response: Response):
    if settings.github_client_id is None or settings.github_client_secret is None:
        raise HTTPException(status_code=501, detail="GitHub-Login isn't available on this server")
    access_token = request.cookies.get("access_token")
    rememberme_token = request.cookies.get("rememberme_token")
    if access_token is not None:
        try:
            data = await check_token(access_token)
            if data is not None:
                return
        except HTTPException:
            pass
    if rememberme_token is not None:
        return await rememberme_check(rememberme_token=rememberme_token, response=response)
    oauth = init_oauth()
    try:
        token = await oauth.github.authorize_access_token(request)
    except authlib.integrations.base_client.OAuthError:
        return RedirectResponse("/account/oauth-error")
    resp = await oauth.github.get("user", token=token)
    data = resp.json()
    user_data = GitHubOauthResponse(**data)
    if user_data.email is None:
        return RedirectResponse("/account/oauth-error?error=email")
        # REGISTER USER
    try:
        await User.objects.create(
            id=uuid.uuid4(),
            email=user_data.email,
            username=user_data.login,
            verified=True,
            auth_type=UserAuthTypes.GITHUB,
            avatar=gzipped_user_avatar(),
        )
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=400, detail="User already exists.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    user = await User.objects.get_or_none(
        email=user_data.email,
        username=user_data.login,
        auth_type=UserAuthTypes.GITHUB,
        verified=True,
    )

    await log_user_in(user=user, request=request, response=response)
    response.headers.append("Location", "/account/login")
    response.status_code = 302
    return response
