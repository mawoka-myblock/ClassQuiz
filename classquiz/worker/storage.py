#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import uuid

import ormar.exceptions
from arq.worker import Retry
import xxhash

from classquiz.config import redis, storage
from tempfile import SpooledTemporaryFile

from classquiz.db.models import StorageItem, Quiz
from classquiz.helpers import extract_image_ids_from_quiz
from classquiz.storage.errors import DeletionFailedError


async def clean_editor_images_up(ctx):
    print("Cleaning images up")
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


async def calculate_hash(ctx, file_id_as_str: str):
    print("Calculating hash")
    file_id = uuid.UUID(file_id_as_str)
    file_data = await StorageItem.objects.get(id=file_id)
    file_path = file_id.hex
    if file_data.storage_path is not None:
        file_path = file_data.storage_path
    file = SpooledTemporaryFile()
    file_bytes = await storage.download(file_path)
    if file_bytes is None:
        print("Retry raised!")
        raise Retry(defer=ctx["job_try"] * 10)
    file.write(file_bytes.getbuffer().tobytes())
    hash_obj = xxhash.xxh3_128()
    # assert hash_obj.block_size == 64
    while chunk := file.read(6400):
        hash_obj.update(chunk)
    file_data.hash = hash_obj.digest()
    print("Got hash!")
    await file_data.update()
    file.close()


async def quiz_update(ctx, old_quiz: Quiz, quiz_id: uuid.UUID):
    new_quiz: Quiz = await Quiz.objects.get(id=quiz_id)
    old_images = extract_image_ids_from_quiz(old_quiz)
    new_images = extract_image_ids_from_quiz(new_quiz)

    # If images are identical, then return
    if sorted(old_images) == sorted(new_images):
        print("Nothing's changed")
        return
    print("Change detected")
    removed_images = list(set(old_images) - set(new_images))
    added_images = list(set(new_images) - set(old_images))
    change_made = False
    # print("added:", added_images)
    # print("removed:", removed_images)
    for image in removed_images:
        if "--" in image:
            await storage.delete([image])
        else:
            item = await StorageItem.objects.get_or_none(id=uuid.UUID(image))
            if item is None:
                continue
            # print("removed item")
            try:
                await new_quiz.storageitems.remove(item)
            except ormar.exceptions.NoMatch:
                continue
            change_made = True
    for image in added_images:
        if "--" not in image:
            item = await StorageItem.objects.get_or_none(id=uuid.UUID(image))
            if item is None:
                continue
            # print("added item")
            await new_quiz.storageitems.add(item)
            change_made = True
    if change_made:
        await new_quiz.update()
