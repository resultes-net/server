"""Add financial parameters.

Adds the parameters of the LCOH calculation (`values.financial` in the JSON
column `parameters.parameters`, see resultes-net/issues#38) to existing
simulations: the EU defaults, with the storage cost curve of the simulation's
system. The values are copied here (and not imported from the client or the
systems code), so that the migration doesn't change when the defaults do.

Revision ID: e9c294e96340
Revises: 84d20633c464
Create Date: 2026-10-07 13:45:05.811982

"""
import json
from typing import Any, Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e9c294e96340'
down_revision: Union[str, None] = '84d20633c464'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Power laws `a * x**b`, in EUR, from section 4.2 of the final report.
_STORAGE_COSTS_BY_SYSTEM_TYPE = {
    'ttes': {'a': 27102, 'b': -0.527},
    'ptes': {'a': 19142, 'b': -0.539},
    'btes': {'a': 472.54, 'b': -0.225},
}

# The final report gives the collector field curve in CHF (eq. 8): converted to EUR with
# the report's localisation factor of 1.24 CHF/EUR.
_COLLECTOR_FIELD_COST = {'a': 1330.12 / 1.24, 'b': -0.0873}


def _create_default_financial_parameters(system_type: str) -> dict[str, Any]:
    return {
        'cost_region': 'eu',
        'real_discount_rate_1': 0.03,
        'fuel_price_per_kWh': 0.08,
        'electricity_price_per_kWh': 0.20,
        'lifetime_a': 30,
        'maintenance_rate_1': 0.01,
        'boiler_efficiency_1': 0.9,
        'storage_cost': _STORAGE_COSTS_BY_SYSTEM_TYPE[system_type],
        'collector_field_cost': _COLLECTOR_FIELD_COST,
        'heat_pump_cost_per_kW': 954.10,
        'boiler_cost_per_kW': 250,
    }


def upgrade() -> None:
    connection = op.get_bind()

    for system_type in _STORAGE_COSTS_BY_SYSTEM_TYPE:
        connection.execute(
            sa.text(
                "UPDATE parameters"
                " SET parameters = jsonb_set(parameters, '{values,financial}', CAST(:financial AS jsonb))"
                " WHERE parameters->'values'->>'type' = :system_type"
            ),
            {'financial': json.dumps(_create_default_financial_parameters(system_type)), 'system_type': system_type},
        )

    n_parameters_without_financial = connection.execute(
        sa.text("SELECT count(*) FROM parameters WHERE parameters->'values'->'financial' IS NULL")
    ).scalar_one()
    if n_parameters_without_financial:
        raise RuntimeError(
            f"{n_parameters_without_financial} simulation(s) have parameters of an unknown system type."
        )


def downgrade() -> None:
    connection = op.get_bind()

    n_parameters_with_changed_financial = 0
    for system_type in _STORAGE_COSTS_BY_SYSTEM_TYPE:
        n_parameters_with_changed_financial += connection.execute(
            sa.text(
                "SELECT count(*) FROM parameters"
                " WHERE parameters->'values'->>'type' = :system_type"
                " AND parameters->'values'->'financial' != CAST(:financial AS jsonb)"
            ),
            {'financial': json.dumps(_create_default_financial_parameters(system_type)), 'system_type': system_type},
        ).scalar_one()

    if n_parameters_with_changed_financial:
        raise RuntimeError(
            f"Can't downgrade: {n_parameters_with_changed_financial} simulation(s) have financial parameters"
            " other than the defaults, which would be lost."
        )

    op.execute("UPDATE parameters SET parameters = parameters #- '{values,financial}'")
