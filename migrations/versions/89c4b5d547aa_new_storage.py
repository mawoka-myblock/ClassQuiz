# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0

"""New storage

Revision ID: 89c4b5d547aa
Revises: 01d7a503e360
Create Date: 2023-05-29 19:24:49.275211

"""
from alembic import op
import sqlalchemy as sa
import ormar
import re
import json

from sqlalchemy.orm import Session
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = "89c4b5d547aa"
down_revision = "8ac2bed1718e"
branch_labels = None
depends_on = None

magic_regex = r"/api/v1/storage/download/(.{36}--.{36})"


def upgrade() -> None:
    ## ADDED STORAGE ITEM
    op.create_table(
        "storage_items",
        sa.Column("id", ormar.fields.sqlalchemy_uuid.CHAR(32), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False),
        sa.Column("mime_type", sa.Text(), nullable=False),
        sa.Column("hash", sa.LargeBinary(length=16), nullable=True),
        sa.Column("user", ormar.fields.sqlalchemy_uuid.CHAR(32), nullable=True),
        sa.Column("size", sa.BigInteger(), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("alt_text", sa.Text(), nullable=True),
        sa.Column("filename", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user"], ["users.id"], name="fk_storage_items_users_id_user"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "storageitems_quizs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("quiz", ormar.fields.sqlalchemy_uuid.CHAR(32), nullable=True),
        sa.Column("storageitem", ormar.fields.sqlalchemy_uuid.CHAR(32), nullable=True),
        sa.ForeignKeyConstraint(
            ["quiz"], ["quiz.id"], name="fk_storageitems_quizs_quiz_quiz_id", onupdate="CASCADE", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["storageitem"],
            ["storage_items.id"],
            name="fk_storageitems_quizs_storage_items_storageitem_id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "storageitems_quiztivitys",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("quiztivity", ormar.fields.sqlalchemy_uuid.CHAR(32), nullable=True),
        sa.Column("storageitem", ormar.fields.sqlalchemy_uuid.CHAR(32), nullable=True),
        sa.ForeignKeyConstraint(
            ["quiztivity"],
            ["quiztivitys.id"],
            name="fk_storageitems_quiztivitys_quiztivitys_quiztivity_id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["storageitem"],
            ["storage_items.id"],
            name="fk_storageitems_quiztivitys_storage_items_storageitem_id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    ## DON'T INCLUDE HOST IN IMAGE URLS
    from classquiz.config import settings

    settings = settings()
    conn = op.get_bind()
    session = Session(bind=conn)
    all_cover_images = session.execute("SELECT cover_image, id from quiz where cover_image is not null;")
    stmt = text("UPDATE quiz SET cover_image = :n WHERE id=:i;")
    for cover_image, id in all_cover_images:
        try:
            new_cover_image = re.search(magic_regex, cover_image).group(1)
            session.execute(stmt, {"n": new_cover_image, "i": id})
        except AttributeError:
            continue

    all_background_images = session.execute("SELECT background_image, id from quiz where background_image is not null;")
    stmt = text("UPDATE quiz SET cover_image = :n WHERE id=:i;")
    for bg_image, id in all_background_images:
        try:
            new_bg_image = re.search(magic_regex, bg_image).group(1)
            session.execute(stmt, {"n": new_bg_image, "i": id})
        except AttributeError:
            continue
    s = text("UPDATE quiz SET questions = :q WHERE id=:i;")

    all_questions = session.execute("SELECT questions, id from quiz;")
    question_image_regex = rf"{settings.root_address}/api/v1/storage/download/(?=.{{36}}--.{{36}})"
    for question, id in all_questions:
        question_as_json = json.dumps(question)
        result = re.sub(question_image_regex, "", question_as_json)
        session.execute(s, {"q": result, "i": id})

    ## ADDED THUMBHASH AND SERVER STORAGE ITEM
    op.add_column("storage_items", sa.Column("thumbhash", sa.Text(), nullable=True))
    op.add_column("storage_items", sa.Column("server", sa.Text(), nullable=True))
    op.add_column("storage_items", sa.Column("imported", sa.Boolean(), nullable=True))

    ## ADDED STORAGE USED TO USER
    op.add_column("users", sa.Column("storage_used", sa.BigInteger(), nullable=True))
    conn = op.get_bind()
    session = Session(bind=conn)
    session.execute("UPDATE users SET storage_used=0 WHERE storage_used is NULL")
    op.alter_column("users", "storage_used", nullable=False)


def downgrade() -> None:
    ## ADDED STORAGE USED TO USER
    op.drop_column("users", "storage_used")

    ## ADDED THUMBHASH AND SERVER STORAGE ITEM
    op.drop_column("storage_items", "imported")
    op.drop_column("storage_items", "server")
    op.drop_column("storage_items", "thumbhash")

    ## DON'T INCLUDE HOST IN IMAGE URLS
    from classquiz.config import settings

    settings = settings()
    conn = op.get_bind()
    session = Session(bind=conn)
    all_cover_images = session.execute("SELECT cover_image, id from quiz where cover_image is not null;")
    stmt = text("UPDATE quiz SET cover_image = :n WHERE id=:i;")
    for cover_image, id in all_cover_images:
        new_cover_image = f"{settings.root_address}/api/v1/storage/download/{cover_image}"
        # print(new_cover_image, id)
        session.execute(stmt, {"n": new_cover_image, "i": id})

    all_background_images = session.execute("SELECT background_image, id from quiz where background_image is not null;")
    stmt = text("UPDATE quiz SET cover_image = :n WHERE id=:i;")
    for bg_image, id in all_background_images:
        new_bg_image = f"{settings.root_address}/api/v1/storage/download/{bg_image}"
        # print(new_cover_image, id)
        session.execute(stmt, {"n": new_bg_image, "i": id})

    all_questions = session.execute("SELECT questions, id from quiz;")
    stmt = text("UPDATE quiz SET questions = :r WHERE id=:i;")
    question_image_regex = r"(?=.{36}--.{36})"
    for question, id in all_questions:
        question_as_json = json.dumps(question)
        result = re.sub(question_image_regex, f"{settings.root_address}/api/v1/storage/download/", question_as_json)
        session.execute(stmt, {"r": result, "i": id})

    ## ADDED STORAGE ITEM
    op.drop_table("storageitems_quiztivitys")
    op.drop_table("storageitems_quizs")
    op.drop_table("storage_items")
