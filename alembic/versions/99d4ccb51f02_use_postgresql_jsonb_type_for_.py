"""Use PostgreSQL JSONB type for parameters field.

Revision ID: 99d4ccb51f02
Revises: c696ad9c570c
Create Date: 2026-07-22 16:26:52.498699

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "99d4ccb51f02"
down_revision: Union[str, None] = "c696ad9c570c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "simulation",
        "parameters",
        existing_type=postgresql.JSON(astext_type=sa.Text()),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=False,
    )


def downgrade() -> None:
    raise NotImplementedError()
