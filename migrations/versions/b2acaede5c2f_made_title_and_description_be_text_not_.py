# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0

"""Made title and description be text not string

Revision ID: b2acaede5c2f
Revises: 400f8ed06c48
Create Date: 2022-12-17 11:31:42.036454

"""
from alembic import op
import sqlalchemy as sa
import ormar


# revision identifiers, used by Alembic.
revision = "b2acaede5c2f"
down_revision = "400f8ed06c48"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("quiz", "title", type_=sa.Text)
    op.alter_column("quiz", "description", type_=sa.Text)


def downgrade() -> None:
    op.alter_column("quiz", "title", type_=sa.String)
    op.alter_column("quiz", "description", type_=sa.String)
