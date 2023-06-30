# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0

"""Added custom_openid

Revision ID: 7afe98d04169
Revises: 438516c09cf3
Create Date: 2023-02-17 15:10:00.158320

"""
from alembic import op
import sqlalchemy as sa
import ormar


# revision identifiers, used by Alembic.
revision = "7afe98d04169"
down_revision = "438516c09cf3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE userauthtypes ADD VALUE 'CUSTOM';")


def downgrade() -> None:
    op.execute("ALTER TYPE userauthtypes DROP VALUE 'CUSTOM';")
