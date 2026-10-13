"""Rename financial lifetime to calculation period.

Renames the financial parameter `lifetime_a` to `calculation_period_a` (in the JSON
column `parameters.parameters`, see resultes-net/issues#43): it's the period over which
the investments are converted into an annuity, not the lifetime of the equipment.

Revision ID: 8655c3168a3e
Revises: e9c294e96340
Create Date: 2026-10-13 10:56:07.956649

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8655c3168a3e'
down_revision: Union[str, None] = 'e9c294e96340'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _rename_financial_key(old_key: str, new_key: str) -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            "UPDATE parameters"
            " SET parameters = jsonb_set("
            "   parameters #- CAST(:old_path AS text[]),"
            "   CAST(:new_path AS text[]),"
            "   parameters->'values'->'financial'->:old_key"
            " )"
            " WHERE parameters->'values'->'financial' ? :old_key"
        ),
        {
            'old_path': f'{{values,financial,{old_key}}}',
            'new_path': f'{{values,financial,{new_key}}}',
            'old_key': old_key,
        },
    )

    n_parameters_without_new_key = connection.execute(
        sa.text("SELECT count(*) FROM parameters WHERE NOT parameters->'values'->'financial' ? :new_key"),
        {'new_key': new_key},
    ).scalar_one()
    if n_parameters_without_new_key:
        raise RuntimeError(
            f"{n_parameters_without_new_key} simulation(s) have financial parameters without `{new_key}`."
        )


def upgrade() -> None:
    _rename_financial_key('lifetime_a', 'calculation_period_a')


def downgrade() -> None:
    _rename_financial_key('calculation_period_a', 'lifetime_a')
