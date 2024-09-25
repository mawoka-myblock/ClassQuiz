# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import uuid

import ormar.exceptions

from classquiz.config import redis, storage

from classquiz.db.models import StorageItem, Quiz, User
from classquiz.helpers import extract_image_ids_from_quiz, extract_music_ids_from_quiz
from classquiz.storage.errors import DeletionFailedError


# skipcq: PYL-W0613
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
    file_id = uuid.UUID(file_id_as_str)
    file_data: StorageItem = await StorageItem.objects.select_related(StorageItem).get(id=file_id)

    user: User | None = await User.objects.get_or_none(id=file_data.id)
    if user is None:
        return
    user.storage_used += file_data.size
    await user.update()


# skipcq: PYL-W0613
async def quiz_update(ctx, old_quiz: Quiz, quiz_id: uuid.UUID):
    new_quiz: Quiz = await Quiz.objects.get(id=quiz_id)
    old_images = extract_image_ids_from_quiz(old_quiz)
    new_images = extract_image_ids_from_quiz(new_quiz)
    old_musics = extract_music_ids_from_quiz(old_quiz)
    new_musics = extract_music_ids_from_quiz(new_quiz)

    # If images are identical, then return
    if sorted(old_images) == sorted(new_images) and sorted(old_musics) == sorted(new_musics):
        print("Nothing's changed")
        return
    print("Change detected")

    removed_images = list(set(old_images) - set(new_images))
    removed_musics = list(set(old_musics) - set(new_musics))
    added_images = list(set(new_images) - set(old_images))
    added_musics = list(set(new_musics) - set(old_musics))

    change_made = False
    for image in removed_images:
        if "--" in image:
            await storage.delete([image])
        else:
            item = await StorageItem.objects.get_or_none(id=uuid.UUID(image))
            if item is None:
                continue
            try:
                await new_quiz.storageitems.remove(item)
            except ormar.exceptions.NoMatch as e:
                print(e)
                continue
            change_made = True
    for music in removed_musics:
        if "--" in music:
            await storage.delete([music])
        else:
            item = await StorageItem.objects.get_or_none(id=uuid.UUID(music))
            if item is None:
                continue
            try:
                await new_quiz.storageitems.remove(item)
            except ormar.exceptions.NoMatch as e:
                print(e)
                continue
            change_made = True
    for image in added_images:
        if "--" not in image:
            item = await StorageItem.objects.get_or_none(id=uuid.UUID(image))
            if item is None:
                continue
            await new_quiz.storageitems.add(item)
            change_made = True
    for music in added_musics:
        if "--" not in music:
            item = await StorageItem.objects.get_or_none(id=uuid.UUID(music))
            if item is None:
                continue
            await new_quiz.storageitems.add(item)
            change_made = True

    if change_made:
        await new_quiz.update()
