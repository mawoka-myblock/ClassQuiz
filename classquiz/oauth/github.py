# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import uuid
from typing import Optional

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
    email: Optional[str]
    node_id: Optional[str]
    avatar_url: Optional[str]
    gravatar_id: Optional[str]
    url: Optional[str]
    html_url: Optional[str]
    followers_url: Optional[str]
    following_url: Optional[str]
    gists_url: Optional[str]
    starred_url: Optional[str]
    subscriptions_url: Optional[str]
    organizations_url: Optional[str]
    repos_url: Optional[str]
    events_url: Optional[str]
    received_events_url: Optional[str]
    type: Optional[str]
    site_admin: Optional[str]
    name: Optional[str]
    company: Optional[str]
    blog: Optional[str]
    location: Optional[str]
    hireable: Optional[bool]
    bio: Optional[str]
    twitter_username: Optional[str]
    public_repos: Optional[int]
    public_gists: Optional[int]
    followers: Optional[int]
    following: Optional[int]
    created_at: datetime
    updated_at: datetime
    private_gists: Optional[int]
    total_private_repos: Optional[int]
    owned_private_repos: Optional[int]
    disk_usage: Optional[int]
    collaborators: Optional[int]
    two_factor_authentication: Optional[bool]
    plan: Optional[Plan]


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
    user_data = GitHubOauthResponse(**resp.json())
    if user_data.email is None:
        return RedirectResponse("/account/oauth-error?error=email")
    user_in_db = await User.objects.get_or_none(email=user_data.email)
    if user_in_db is None:
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
        # skipcq: PYL-W0703
        except Exception as e:
            if type(e) is asyncpg.exceptions.UniqueViolationError:
                error = True
                counter = 1
                while error:
                    try:
                        await User.objects.create(
                            id=uuid.uuid4(),
                            email=user_data.email,
                            username=user_data.login,
                            verified=True,
                            auth_type=UserAuthTypes.GITHUB,
                            avatar=gzipped_user_avatar(),
                        )
                        error = False
                    except asyncpg.exceptions.UniqueViolationError:
                        counter += 1
                        error = True
            else:
                raise HTTPException(status_code=500, detail=str(e))
    user = await User.objects.get_or_none(
        email=user_data.email, username=user_data.login, auth_type=UserAuthTypes.GITHUB, verified=True
    )

    await log_user_in(user=user, request=request, response=response)
    response.headers.append("Location", "/account/login")
    response.status_code = 302
    return response
