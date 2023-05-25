"""Dont include host in image urls anymore

Revision ID: b74382b2c6ad
Revises: 44255816ff7b
Create Date: 2023-05-25 16:25:11.646113

"""
import json
import re

from alembic import op
import sqlalchemy as sa
import ormar
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision = "b74382b2c6ad"
down_revision = "44255816ff7b"
branch_labels = None
depends_on = None

magic_regex = r"/api/v1/storage/download/(.{36}--.{36})"


def upgrade() -> None:
    from classquiz.config import settings

    settings = settings()
    conn = op.get_bind()
    session = Session(bind=conn)
    all_cover_images = session.execute("SELECT cover_image, id from quiz where cover_image is not null;")
    for cover_image, id in all_cover_images:
        new_cover_image = re.search(magic_regex, cover_image).group(1)
        # print(new_cover_image, id)
        session.execute(f"UPDATE quiz SET cover_image = '{new_cover_image}' WHERE id='{id}';")

    all_background_images = session.execute("SELECT background_image, id from quiz where background_image is not null;")
    for bg_image, id in all_background_images:
        new_bg_image = re.search(magic_regex, bg_image).group(1)
        # print(new_cover_image, id)
        session.execute(f"UPDATE quiz SET cover_image = '{new_bg_image}' WHERE id='{id}';")

    all_questions = session.execute("SELECT questions, id from quiz;")
    question_image_regex = rf"{settings.root_address}/api/v1/storage/download/(?=.{{36}}--.{{36}})"
    for question, id in all_questions:
        question_as_json = json.dumps(question)
        result = re.sub(question_image_regex, "", question_as_json)
        session.execute(f"UPDATE quiz SET questions = '{result}' WHERE id='{id}';")


def downgrade() -> None:
    from classquiz.config import settings

    settings = settings()
    conn = op.get_bind()
    session = Session(bind=conn)
    all_cover_images = session.execute("SELECT cover_image, id from quiz where cover_image is not null;")
    for cover_image, id in all_cover_images:
        new_cover_image = f"{settings.root_address}/api/v1/storage/download/{cover_image}"
        # print(new_cover_image, id)
        session.execute(f"UPDATE quiz SET cover_image = '{new_cover_image}' WHERE id='{id}';")

    all_background_images = session.execute("SELECT background_image, id from quiz where background_image is not null;")
    for bg_image, id in all_background_images:
        new_bg_image = f"{settings.root_address}/api/v1/storage/download/{bg_image}"
        # print(new_cover_image, id)
        session.execute(f"UPDATE quiz SET cover_image = '{new_bg_image}' WHERE id='{id}';")

    all_questions = session.execute("SELECT questions, id from quiz;")
    question_image_regex = r"(?=.{36}--.{36})"
    for question, id in all_questions:
        question_as_json = json.dumps(question)
        result = re.sub(question_image_regex, f"{settings.root_address}/api/v1/storage/download", question_as_json)
        session.execute(f"UPDATE quiz SET questions = '{result}' WHERE id='{id}';")
