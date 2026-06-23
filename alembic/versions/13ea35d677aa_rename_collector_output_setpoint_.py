"""Rename collector output setpoint temperature.

Revision ID: 13ea35d677aa
Revises: 9338efb4acae
Create Date: 2026-06-23 15:27:10.125650

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

import copy
import sqlalchemy.orm as orm
import sqlalchemy.orm.session as sess

# revision identifiers, used by Alembic.
revision: str = "13ea35d677aa"
down_revision: Union[str, None] = "9338efb4acae"
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

            collector_output_setpoint_degC = parameters["values"]["temperatures"].pop(
                "output_temperature_setpoint_degC"
            )

            parameters["values"]["temperatures"][
                "collector_output_setpoint_degC"
            ] = collector_output_setpoint_degC

            simulation.parameters = parameters

        session.commit()


def downgrade() -> None:
    statement = sa.select(Simulation).where(
        Simulation.parameters["values"]["type"].as_string() == "ptes",
    )

    with sess.Session(bind=op.get_bind()) as session:
        simulations = session.scalars(statement)

        for simulation in simulations:
            parameters = copy.deepcopy(simulation.parameters)

            output_temperature_setpoint_degC = parameters["values"]["temperatures"].pop(
                "collector_output_setpoint_degC"
            )
            
            parameters["values"]["temperatures"][
                "output_temperature_setpoint_degC"
            ] = output_temperature_setpoint_degC

            simulation.parameters = parameters

        session.commit()
