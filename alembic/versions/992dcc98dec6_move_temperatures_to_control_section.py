"""Move temperatures to control section.

Revision ID: 992dcc98dec6
Revises: a57548945a07
Create Date: 2026-07-06 15:18:41.437532

"""

import copy
from typing import Sequence, Union

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy.orm.session as sess
import sqlmodel

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "992dcc98dec6"
down_revision: Union[str, None] = "a57548945a07"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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

            temperatures = parameters["values"].pop("temperatures")

            control = {
                "demand_temperature_setpoint_degC": temperatures[
                    "demand_setpoint_degC"
                ],
                "demand_delta_T_degC": 30.0,
                "storage_temperature_maximum_degC": temperatures[
                    "storage_maximum_degC"
                ],
            }

            parameters["values"]["control"] = control
            simulation.parameters = parameters

        session.commit()


def downgrade() -> None:
    raise NotImplementedError()
