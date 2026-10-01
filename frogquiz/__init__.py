# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from socketio import ASGIApp
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

import logging

from frogquiz.config import settings, MAX_UPLOAD_SIZE
from frogquiz.db import database

from frogquiz.oauth import rememberme_middleware
from frogquiz.routers import (
    users,
    quiz,
    utils,
    stats,
    storage,
    search,
    testing_routes,
    editor,
    live,
    eximport,
    login,
    sitemap,
    remote,
    community,
    avatar,
    results,
    admin,
    box_controller,
    quiztivity,
    pixabay,
    moderation,
)
from frogquiz.socket_server import sio
from frogquiz.helpers import meilisearch_init

settings = settings()
app = FastAPI(redoc_url="", docs_url="/api/docs")
app.state.database = database


@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()
    # Search is not on the critical path: a game needs Postgres and Redis, not
    # the index. Previously an unreachable Meilisearch aborted startup entirely,
    # so a search outage took the live game loop down with it.
    try:
        await meilisearch_init()
    except Exception as e:  # noqa: BLE001 - any failure here must stay non-fatal
        logging.getLogger("frogquiz").warning(
            "MeiliSearch unavailable at startup (%s); search will be degraded until it returns.", e
        )
    # Said once, loudly, at boot: a misconfigured relay is otherwise invisible
    # until someone can't get back into their account.
    if not settings.mail_configured:
        logging.getLogger("frogquiz").warning(
            "No mail server configured (MAIL_SERVER/MAIL_ADDRESS). "
            "Password recovery is unavailable%s.",
            ""
            if settings.skip_email_verification
            else ", and registration will fail because SKIP_EMAIL_VERIFICATION is False",
        )


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()


@app.middleware("http")
async def auth_middleware_wrapper(request: Request, call_next):
    return await rememberme_middleware(request, call_next)


# Largest body any upload route will accept, plus room for the multipart framing around
# it (boundaries, headers, the filename).
_UPLOAD_ENVELOPE_SLACK = 64 * 1024


@app.middleware("http")
async def request_size_guard(request: Request, call_next):
    """Refuse an oversized upload on its Content-Length, before the body is read.

    The route's own check is the authoritative one, but it only runs once FastAPI has
    parsed the multipart body -- and Starlette spools a part past 1MB to a temp file, so
    a 2GB upload is 2GB written to disk before any Python of ours sees it. This costs one
    header lookup and makes the common case cheap. It is not the whole defence: a client
    can omit Content-Length or lie about it, which is what the route check is for, and
    the Caddyfile caps the body at the edge for the case where neither has run yet.
    """
    if request.method == "POST" and request.url.path.startswith("/api/v1/storage"):
        declared = request.headers.get("content-length")
        if declared is not None and declared.isdigit():
            if int(declared) > MAX_UPLOAD_SIZE + _UPLOAD_ENVELOPE_SLACK:
                return JSONResponse(
                    status_code=413,
                    content={"detail": f"File is too large: limit is {MAX_UPLOAD_SIZE} bytes"},
                )
    return await call_next(request)


app.include_router(
    moderation.router,
    tags=["moderation"],
    prefix="/api/v1/moderation",
    include_in_schema=True,
)
app.include_router(pixabay.router, tags=["pixabay"], prefix="/api/v1/pixabay", include_in_schema=True)
if settings.enable_quiztivity:
    app.include_router(
        quiztivity.router,
        tags=["quiztivity"],
        prefix="/api/v1/quiztivity",
        include_in_schema=True,
    )

if settings.enable_box_controller:
    app.include_router(
        box_controller.router,
        tags=["boxcontroller"],
        prefix="/api/v1/box-controller",
        include_in_schema=True,
    )
app.include_router(results.router, tags=["results"], prefix="/api/v1/results", include_in_schema=True)
app.include_router(remote.router, tags=["remote"], prefix="/api/v1/remote", include_in_schema=True)
app.include_router(login.router, tags=["auth"], prefix="/api/v1/login", include_in_schema=True)

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)


class ApiOnlyCORSMiddleware(CORSMiddleware):
    """CORS for the REST API only.

    socket.io sets its own CORS headers, and two Access-Control-Allow-Origin
    headers on one response make browsers reject it outright.
    """

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"].startswith("/socket.io"):
            return await self.app(scope, receive, send)
        return await super().__call__(scope, receive, send)


if settings.cors_origins:
    app.add_middleware(
        ApiOnlyCORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
app.include_router(users.router, tags=["users"], prefix="/api/v1/users", include_in_schema=True)
app.include_router(quiz.router, tags=["quiz"], prefix="/api/v1/quiz", include_in_schema=True)
app.include_router(utils.router, tags=["utils"], prefix="/api/v1/utils", include_in_schema=True)
app.include_router(stats.router, tags=["stats"], prefix="/api/v1/stats", include_in_schema=True)
app.include_router(storage.router, tags=["storage"], prefix="/api/v1/storage", include_in_schema=True)
app.include_router(search.router, tags=["search"], prefix="/api/v1/search", include_in_schema=True)
app.include_router(live.router, tags=["live"], prefix="/api/v1/live", include_in_schema=True)
if settings.enable_testing_routes:
    app.include_router(
        testing_routes.router,
        tags=["internal", "testing"],
        prefix="/api/v1/internal/testing",
        include_in_schema=False,
    )
app.include_router(editor.router, tags=["editor"], prefix="/api/v1/editor", include_in_schema=True)
app.include_router(
    eximport.router,
    tags=["export", "import"],
    prefix="/api/v1/eximport",
    include_in_schema=True,
)
app.include_router(sitemap.router, tags=["sitemap"], prefix="/api/v1/sitemap", include_in_schema=True)
app.include_router(
    community.router,
    tags=["community"],
    prefix="/api/v1/community",
    include_in_schema=True,
)
app.include_router(avatar.router, tags=["avatar"], prefix="/api/v1/avatar", include_in_schema=True)
app.include_router(admin.router, tags=["admin"], prefix="/api/v1/admin", include_in_schema=True)
app.mount("/", ASGIApp(sio))
