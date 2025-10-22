"""Add optional notes column."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("audit_entries", sa.Column("notes", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("audit_entries", "notes")
