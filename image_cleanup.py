# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0

import asyncio

from classquiz.config import settings, redis, storage
from classquiz.storage.errors import DeletionFailedError

settings = settings()


async def main():
    edit_sessions = await redis.smembers("edit_sessions")
    for session_id in edit_sessions:
        session = await redis.get(f"edit_session:{session_id}")
        if session is None:
            images = await redis.lrange(f"edit_session:{session_id}:images", 0, 3000)
            if len(images) != 0:
                try:
                    await storage.delete(images)
                except DeletionFailedError:
                    print("Deletion Error", images)
            await redis.srem("edit_sessions", session_id)
            await redis.delete(f"edit_session:{session_id}:images")


if __name__ == "__main__":
    asyncio.run(main())
