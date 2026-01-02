"""Insert singleton row into last login table.

Revision ID: 7db9a82dda48
Revises: 8f9079e2195c
Create Date: 2026-01-02 19:32:09.035052

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

import datetime as dt


# revision identifiers, used by Alembic.
revision: str = "7db9a82dda48"
down_revision: Union[str, None] = "8f9079e2195c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    table = sa.table(
        "latestlogin", sa.Column("on", sa.DateTime(timezone=True), nullable=False)
    )
    op.bulk_insert(table, [dict(on=dt.datetime.min)])


def downgrade() -> None:
    op.execute("DELETE FROM lastlogin")
