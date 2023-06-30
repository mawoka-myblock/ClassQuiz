# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0

"""Added Controllers Table

Revision ID: 32649a1ffcf2
Revises: 89c4b5d547aa
Create Date: 2023-06-30 01:24:43.124764

"""
from alembic import op
import sqlalchemy as sa
import ormar

# revision identifiers, used by Alembic.
revision = "32649a1ffcf2"
down_revision = "89c4b5d547aa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "controller",
        sa.Column("id", ormar.fields.sqlalchemy_uuid.CHAR(32), nullable=False),
        sa.Column("user", ormar.fields.sqlalchemy_uuid.CHAR(32), nullable=True),
        sa.Column("secret_key", sa.String(length=24), nullable=False),
        sa.Column("player_name", sa.Text(), nullable=False),
        sa.Column("last_seen", sa.DateTime(), nullable=True),
        sa.Column("first_seen", sa.DateTime(), nullable=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("os_version", sa.Text(), nullable=True),
        sa.Column("wanted_os_version", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user"], ["users.id"], name="fk_controller_users_id_user"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("controller")
