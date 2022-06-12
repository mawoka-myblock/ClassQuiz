from fastapi import APIRouter, Request, HTTPException, Response
from classquiz.config import settings

from classquiz.db.models import User, UserAuthTypes
from pydantic import BaseModel
from classquiz.auth import check_token
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
    node_id: str
    avatar_url: str
    gravatar_id: str
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: bool
    name: str
    company: None
    blog: str
    location: str
    email: str
    hireable: None
    bio: str
    twitter_username: str
    public_repos: int
    public_gists: int
    followers: int
    following: int
    created_at: datetime
    updated_at: datetime
    private_gists: int
    total_private_repos: int
    owned_private_repos: int
    disk_usage: int
    collaborators: int
    two_factor_authentication: bool
    plan: Plan


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
    token = await oauth.github.authorize_access_token(request)
    resp = await oauth.github.get("user", token=token)
    user_data = GitHubOauthResponse(**resp.json())
    user_in_db = await User.objects.get_or_none(email=user_data.email)
    if user_in_db is None:
        # REGISTER USER
        create_user = User(
            email=user_data.email,
            username=user_data.login,
            verified=True,
            auth_type=UserAuthTypes.GITHUB,
        )
        try:
            await create_user.save()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    user = await User.objects.get_or_none(
        email=user_data.email, username=user_data.login, auth_type=UserAuthTypes.GITHUB, verified=True
    )

    await log_user_in(user=user, request=request, response=response)
    response.headers.append("Location", "/account/login")
    response.status_code = 302
    return response
