"""Add collector output setpoint temperature to parameters.

Revision ID: 89ac88c2d2e9
Revises: 0aa753691930
Create Date: 2026-06-10 14:21:37.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

import copy
import sqlalchemy.orm as orm
import sqlalchemy.orm.session as sess


# revision identifiers, used by Alembic.
revision: str = "89ac88c2d2e9"
down_revision: Union[str, None] = "0aa753691930"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

Base = orm.declarative_base()


class Simulation(Base):
    __tablename__ = "simulation"

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    parameters = sa.Column(sa.JSON)


OUTPUT_TEMPERATURE_SETPOINT_DEGC_BY_TYPE = {
    "ptes": 100.0,
    "ttes": 95.0,
}


def upgrade() -> None:
    statement = sa.select(Simulation)

    with sess.Session(bind=op.get_bind()) as session:
        simulations = session.scalars(statement)

        for simulation in simulations:
            parameters = copy.deepcopy(simulation.parameters)

            values = parameters["values"]
            collector_field = values["collector_field"]

            if "output_temperature_setpoint_degC" in collector_field:
                continue

            collector_field["output_temperature_setpoint_degC"] = (
                OUTPUT_TEMPERATURE_SETPOINT_DEGC_BY_TYPE[values["type"]]
            )

            simulation.parameters = parameters

        session.commit()


def downgrade() -> None:
    statement = sa.select(Simulation)

    with sess.Session(bind=op.get_bind()) as session:
        simulations = session.scalars(statement)

        for simulation in simulations:
            parameters = copy.deepcopy(simulation.parameters)

            parameters["values"]["collector_field"].pop(
                "output_temperature_setpoint_degC", None
            )

            simulation.parameters = parameters

        session.commit()
