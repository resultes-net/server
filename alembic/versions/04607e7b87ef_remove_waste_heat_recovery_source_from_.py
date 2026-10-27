"""Remove waste heat recovery source from BTES parameters

BTES doesn't simulate a waste heat recovery source, so `waste_heat_recovery_source` was
moved from the parameters common to all systems to those of TTES and PTES (in the JSON
column `parameters.parameters`, see https://github.com/resultes-net/issues/issues/61).
The downgrade re-adds the client's default (`createDefaultWasteHeatRecoverySource`, stored with
floats like the server does), which all BTES simulations had.

Revision ID: 04607e7b87ef
Revises: 8655c3168a3e
Create Date: 2026-10-27 08:20:29.128712

"""
from typing import Sequence, Union

import json

from alembic import op
import sqlalchemy as sa
import sqlmodel



# revision identifiers, used by Alembic.
revision: str = '04607e7b87ef'
down_revision: Union[str, None] = '8655c3168a3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_N_HOURS_PER_YEAR = 365 * 24

_DEFAULT_WASTE_HEAT_RECOVERY_SOURCE = {
    'name': '<disabled>',
    'mass_flow_rates_kg_per_h': [0.0] * _N_HOURS_PER_YEAR,
    'temperatures_deg_C': [0.0] * _N_HOURS_PER_YEAR,
}

_IS_BTES = "parameters->'values'->>'type' = 'btes'"

_HAS_WASTE_HEAT_RECOVERY_SOURCE = "parameters->'values' ? 'waste_heat_recovery_source'"


def _check_btes_parameters(*, shall_have_source: bool) -> None:
    connection = op.get_bind()

    n_btes_parameters = connection.execute(
        sa.text(f"SELECT count(*) FROM parameters WHERE {_IS_BTES}")
    ).scalar_one()
    n_btes_parameters_with_source = connection.execute(
        sa.text(f"SELECT count(*) FROM parameters WHERE {_IS_BTES} AND {_HAS_WASTE_HEAT_RECOVERY_SOURCE}")
    ).scalar_one()

    n_expected = n_btes_parameters if shall_have_source else 0
    if n_btes_parameters_with_source != n_expected:
        raise RuntimeError(
            f"{n_btes_parameters_with_source} of {n_btes_parameters} BTES simulation(s) have a waste heat"
            f" recovery source, expected {n_expected}."
        )


def upgrade() -> None:
    op.get_bind().execute(
        sa.text(
            "UPDATE parameters"
            " SET parameters = parameters #- '{values,waste_heat_recovery_source}'"
            f" WHERE {_IS_BTES}"
        )
    )

    _check_btes_parameters(shall_have_source=False)


def downgrade() -> None:
    op.get_bind().execute(
        sa.text(
            "UPDATE parameters"
            " SET parameters = jsonb_set("
            "   parameters, '{values,waste_heat_recovery_source}', CAST(:source AS jsonb)"
            " )"
            f" WHERE {_IS_BTES}"
        ),
        {'source': json.dumps(_DEFAULT_WASTE_HEAT_RECOVERY_SOURCE)},
    )

    _check_btes_parameters(shall_have_source=True)
