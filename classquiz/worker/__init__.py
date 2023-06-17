#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
from arq import cron
from arq.connections import RedisSettings

from classquiz import settings
from classquiz.db import database
from classquiz.worker.storage import clean_editor_images_up, calculate_hash, quiz_update


async def startup(ctx):
    ctx["db"] = database
    if not ctx["db"].is_connected:
        await ctx["db"].connect()


async def shutdown(ctx):
    if ctx["db"].is_connected:
        await ctx["db"].disconnect()


class WorkerSettings:
    functions = [calculate_hash, quiz_update]
    cron_jobs = [cron(clean_editor_images_up, hour={0, 6, 12, 18}, minute=0)]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.redis)
