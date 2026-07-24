"""Add profile for waste heat recovery source.

Revision ID: 91be872c85d0
Revises: 471ed5924498
Create Date: 2026-07-22 08:55:53.016581

"""

import copy
from typing import Sequence, Union

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy.orm.session as sess
import sqlmodel

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "91be872c85d0"
down_revision: Union[str, None] = "471ed5924498"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


WASTE_HEAT_RECOVERY_SOURCE = {
    "name": "<disabled>",
    "hourly_values": [
        {"mass_flow_rate_kg_per_h": 0, "temperature_deg_C": 0} for _ in range(365 * 24)
    ],
}


Base = orm.declarative_base()


class Simulation(Base):
    __tablename__ = "simulation"

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    parameters = sa.Column(sa.JSON)


def upgrade() -> None:
    statement = sa.select(Simulation).where(
        Simulation.parameters["values"]["type"].as_string() == "ptes",
    )

    with sess.Session(bind=op.get_bind()) as session:
        simulations = session.scalars(statement)

        for simulation in simulations:
            parameters = copy.deepcopy(simulation.parameters)

            parameters["values"][
                "waste_heat_recovery_source"
            ] = WASTE_HEAT_RECOVERY_SOURCE

            simulation.parameters = parameters

        session.commit()


def downgrade() -> None:
    raise NotImplementedError()
