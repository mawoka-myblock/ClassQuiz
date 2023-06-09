#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import io
import json
import uuid
from datetime import datetime

import ormar.exceptions
from aiohttp import ClientSession
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from classquiz.auth import get_current_user
from classquiz.config import storage, settings, arq
from classquiz.db.models import Quiz, User, StorageItem
import gzip
import urllib.parse
import magic

router = APIRouter()
settings = settings()
quiz_delimiter = b"\xc7\xc7\xc7\x00"
image_delimiter = b"\xc6\xc6\xc6\x00"
image_index_delimiter = b"\xc5\xc5\x00"


@router.get("/{quiz_id}")
async def export_quiz(quiz_id: uuid.UUID, user: User = Depends(get_current_user)):
    try:
        quiz: Quiz = await Quiz.objects.filter(Quiz.id == quiz_id).first()
    except ormar.exceptions.NoMatch:
        raise HTTPException(status_code=404, detail="Quiz not found")
    image_urls = {}
    for i, question in enumerate(quiz.questions):
        if question["image"] is None:
            continue
        else:
            image_urls[i] = question["image"]
            question["image"] = i
    if quiz.cover_image is not None:
        image_urls[-1] = quiz.cover_image
        quiz.cover_image = -1
    quiz_dict = quiz.dict()
    del quiz_dict["user_id"], quiz_dict["id"]
    quiz_dict["created_at"] = quiz_dict["created_at"].isoformat()
    quiz_dict["updated_at"] = quiz_dict["updated_at"].isoformat()
    quiz_json = json.dumps(quiz_dict)
    bin_data = gzip.compress(quiz_json.encode("utf-8"), compresslevel=9)
    # bin_data = quiz_json.encode("utf-8")
    bin_data = bin_data + quiz_delimiter
    for image_key in image_urls.keys():
        bin_data = bin_data + image_delimiter + str(image_key).encode("utf-8") + image_index_delimiter
        image_data = None
        async with ClientSession() as session, session.get(
            f"{settings.root_address}/api/v1/storage/download/{image_urls[image_key]}"
        ) as resp:
            image_data = await resp.read()
        bin_data = bin_data + image_data

    def stream_response():
        yield bin_data

    return StreamingResponse(
        stream_response(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment;filename={urllib.parse.quote(quiz.title)}.cqa"
            # noqa: E501
        },
    )


@router.post("/")
async def import_quiz(file: UploadFile = File(), user: User = Depends(get_current_user)):
    if user.storage_used > settings.free_storage_limit:
        raise HTTPException(status_code=409, detail="Storage limit reached")
    data = await file.read()
    [split_data, images] = data.split(quiz_delimiter)
    decompressed_quiz = gzip.decompress(split_data)
    quiz_dict = json.loads(decompressed_quiz.decode("utf-8"))
    image_splits = images.split(image_delimiter)
    quiz_id = uuid.uuid4()
    image_urls = {}
    print(len(data))
    for image_split in image_splits:
        res = image_split.split(image_index_delimiter)
        if len(res) != 2:
            continue
        [index, image_data] = res
        print(len(image_data))
        img_data = io.BytesIO(image_data)
        mime_type = magic.from_buffer(img_data.read(2048), mime=True)
        print(mime_type)
        index = int(index.decode("utf-8"))
        file_id = uuid.uuid4()
        file_obj = StorageItem(
            id=file_id,
            uploaded_at=datetime.now(),
            mime_type=mime_type,
            hash=None,
            user=user,
            size=0,
            deleted_at=None,
            alt_text=None,
        )
        await storage.upload(file_name=file_id.hex, file_data=img_data, mime_type=mime_type)
        await file_obj.save()
        await arq.enqueue_job("calculate_hash", file_id.hex)
        image = file_id.hex
        image_urls[index] = image
    quiz_dict["created_at"] = datetime.fromisoformat(quiz_dict["created_at"])
    quiz_dict["updated_at"] = datetime.fromisoformat(quiz_dict["updated_at"])
    quiz_dict["id"] = quiz_id
    for question in quiz_dict["questions"]:
        if question["image"] is not None:
            question["image"] = image_urls[question["image"]]
    if quiz_dict["cover_image"] is not None:
        quiz_dict["cover_image"] = image_urls[-1]
    quiz = Quiz.parse_obj(quiz_dict)
    quiz.user_id = user.id
    quiz.imported_from_kahoot = None
    await quiz.save()
    return quiz
