# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0

import sentry_sdk
from fastapi import FastAPI, Request
from sentry_sdk.integrations.redis import RedisIntegration
from socketio import ASGIApp
from starlette.middleware.sessions import SessionMiddleware

from classquiz.config import settings
from classquiz.db import database

from classquiz.oauth import rememberme_middleware
from classquiz.routers import (
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
from classquiz.socket_server import sio
from classquiz.helpers import meilisearch_init, telemetry_ping

settings = settings()
if settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn, integrations=[RedisIntegration()])
app = FastAPI(redoc_url="", docs_url="/api/docs")
app.state.database = database


@app.middleware("http")
async def sentry_exception(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        with sentry_sdk.push_scope() as scope:
            scope.set_context("request", request)
            sentry_sdk.capture_exception(e)
        raise e


@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()
    await meilisearch_init()
    await telemetry_ping()


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()


@app.middleware("http")
async def auth_middleware_wrapper(request: Request, call_next):
    return await rememberme_middleware(request, call_next)


app.include_router(moderation.router, tags=["moderation"], prefix="/api/v1/moderation", include_in_schema=True)
app.include_router(pixabay.router, tags=["pixabay"], prefix="/api/v1/pixabay", include_in_schema=True)
app.include_router(quiztivity.router, tags=["quiztivity"], prefix="/api/v1/quiztivity", include_in_schema=True)

app.include_router(
    box_controller.router, tags=["boxcontroller"], prefix="/api/v1/box-controller", include_in_schema=True
)
app.include_router(results.router, tags=["results"], prefix="/api/v1/results", include_in_schema=True)
app.include_router(remote.router, tags=["remote"], prefix="/api/v1/remote", include_in_schema=True)
app.include_router(login.router, tags=["auth"], prefix="/api/v1/login", include_in_schema=True)

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.include_router(users.router, tags=["users"], prefix="/api/v1/users", include_in_schema=True)
app.include_router(quiz.router, tags=["quiz"], prefix="/api/v1/quiz", include_in_schema=True)
app.include_router(utils.router, tags=["utils"], prefix="/api/v1/utils", include_in_schema=True)
app.include_router(stats.router, tags=["stats"], prefix="/api/v1/stats", include_in_schema=True)
app.include_router(storage.router, tags=["storage"], prefix="/api/v1/storage", include_in_schema=True)
app.include_router(search.router, tags=["search"], prefix="/api/v1/search", include_in_schema=True),
app.include_router(live.router, tags=["live"], prefix="/api/v1/live", include_in_schema=True)
app.include_router(
    testing_routes.router, tags=["internal", "testing"], prefix="/api/v1/internal/testing", include_in_schema=False
)
app.include_router(editor.router, tags=["editor"], prefix="/api/v1/editor", include_in_schema=True)
app.include_router(eximport.router, tags=["export", "import"], prefix="/api/v1/eximport", include_in_schema=True)
app.include_router(sitemap.router, tags=["sitemap"], prefix="/api/v1/sitemap", include_in_schema=True)
app.include_router(community.router, tags=["community"], prefix="/api/v1/community", include_in_schema=True)
app.include_router(avatar.router, tags=["avatar"], prefix="/api/v1/avatar", include_in_schema=True)
app.include_router(admin.router, tags=["admin"], prefix="/api/v1/admin", include_in_schema=True)
app.mount("/", ASGIApp(sio))
