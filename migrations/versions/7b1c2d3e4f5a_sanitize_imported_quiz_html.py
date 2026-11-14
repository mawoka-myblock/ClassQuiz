# SPDX-License-Identifier: MPL-2.0

"""sanitize quiz html that bypassed the editor

The .cqa and Excel imports stored titles, descriptions, questions and answers
without the editor's HTML sanitizer, and the frontend renders these fields as
HTML. Re-apply the editor's sanitization to every stored quiz and saved game
result. Text saved through the editor is already clean and comes out unchanged,
so only rows that actually change are written.

Revision ID: 7b1c2d3e4f5a
Revises: 9d7fa2e6b24c
Create Date: 2026-11-12 12:00:00.000000

"""

import json

import sqlalchemy as sa
from alembic import op

from classquiz.helpers import sanitize_quiz_dict

# revision identifiers, used by Alembic.
revision = "7b1c2d3e4f5a"
down_revision = "9d7fa2e6b24c"
branch_labels = None
depends_on = None


def _sanitize_table(conn, table: str) -> None:
    rows = conn.execute(sa.text(f"SELECT id, title, description, questions FROM {table}")).fetchall()
    for row_id, title, description, questions in rows:
        if isinstance(questions, str):
            questions = json.loads(questions)
        before = {"title": title, "description": description, "questions": questions}
        after = sanitize_quiz_dict(json.loads(json.dumps(before)))
        if after != before:
            conn.execute(
                sa.text(
                    f"UPDATE {table} SET title = :t, description = :d, questions = CAST(:q AS json) WHERE id = :id"
                ),
                {"t": after["title"], "d": after["description"], "q": json.dumps(after["questions"]), "id": row_id},
            )


def upgrade() -> None:
    conn = op.get_bind()
    _sanitize_table(conn, "quiz")
    _sanitize_table(conn, "game_results")


def downgrade() -> None:
    # Removed markup is not restored.
    pass
