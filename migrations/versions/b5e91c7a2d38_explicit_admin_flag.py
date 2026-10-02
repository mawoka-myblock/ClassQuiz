# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0

"""Explicit admin flag

`get_admin_user` resolved the instance admin as "the account with the oldest
created_at". Nothing recorded the role, so deleting that account silently
promoted whoever had registered next -- and account deletion became reachable
from the UI in c3f8a1d47b62's change, which turns a latent oddity into
something a person can trigger by tidying up their own account.

This adds `users.is_admin` and sets it on exactly the account the old rule was
already pointing at, so the role does not change hands when this ships. After
that the flag is the only thing that grants admin, and it moves only when
somebody moves it.

Note the ordering: the backfill has to run before anyone is deleted, which is
why it is part of the same migration rather than a follow-up.

Revision ID: b5e91c7a2d38
Revises: c3f8a1d47b62
Create Date: 2026-09-16 09:40:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "b5e91c7a2d38"
down_revision = "c3f8a1d47b62"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    # Exactly what get_admin_user used to compute, frozen into a column. Scoped to a
    # single id so a tie on created_at cannot promote two accounts.
    op.execute("""
        UPDATE users SET is_admin = true
        WHERE id = (SELECT id FROM users ORDER BY created_at ASC LIMIT 1)
        """)


def downgrade() -> None:
    # Dropping the column restores the old "oldest account wins" behaviour, since
    # that logic is what the flag replaced.
    op.drop_column("users", "is_admin")
