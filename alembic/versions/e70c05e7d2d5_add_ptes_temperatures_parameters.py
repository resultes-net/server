"""Add PTES temperatures parameters to existing simulations.

This migration adds the missing 'temperatures' field to PTES simulations
to support the new Temperatures model in PtesParameters.

The temperatures are:
- demand_setpoint_degC: 80.0 (TSetDem)
- boiler_output_setpoint_degC: 80.0 (TSetBolr = TSetDem)
- heat_pump_output_setpoint_degC: 80.0 (TSetHp = TSetDem)
- storage_maximum_degC: 85.0 (TTesMax)

These defaults match the values previously hardcoded in the ddcks:
- TSetDem = 50 was hardcoded in PTES/ddck/control/control.ddck
- TTesMax = 95 was hardcoded in common/ddck/SolarControl/Stagnation.ddck

But the new system expects these to be configurable from the UI, with defaults
matching the research config behavior: TSetBolr = TSetHp = TSetDem = 80, TTesMax = 85.

Revision ID: e70c05e7d2d5
Revises: 89ac88c2d2e9
Create Date: 2026-06-15 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

import copy
import sqlalchemy.orm as orm
import sqlalchemy.orm.session as sess


# revision identifiers, used by Alembic.
revision: str = "e70c05e7d2d5"
down_revision: Union[str, None] = "89ac88c2d2e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

Base = orm.declarative_base()


class Simulation(Base):
    __tablename__ = "simulation"

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    parameters = sa.Column(sa.JSON)


# Default temperature values based on the research config behavior
# These match the defaults that will be used in the UI
DEFAULT_TEMPERATURES = {
    "demand_setpoint_degC": 80.0,
    "boiler_output_setpoint_degC": 80.0,
    "heat_pump_output_setpoint_degC": 80.0,
    "storage_maximum_degC": 85.0,
}


def upgrade() -> None:
    # Select only PTES simulations that are missing the 'temperatures' field
    statement = sa.select(Simulation).where(
        Simulation.parameters['values']['type'].astext == 'ptes',
        Simulation.parameters['values']['temperatures'].astext == None
    )

    with sess.Session(bind=op.get_bind()) as session:
        simulations = session.scalars(statement)

        for simulation in simulations:
            parameters = copy.deepcopy(simulation.parameters)

            # We already filtered for dict structure in the where clause, 
            # but keep basic safety check
            if not isinstance(parameters, dict):
                continue

            values = parameters.get("values", {})
            if not isinstance(values, dict):
                continue

            # Add the temperatures field with default values
            values["temperatures"] = DEFAULT_TEMPERATURES
            parameters["values"] = values

            simulation.parameters = parameters

        session.commit()


def downgrade() -> None:
    # Select only PTES simulations that have the 'temperatures' field
    statement = sa.select(Simulation).where(
        Simulation.parameters['values']['type'].astext == 'ptes',
        Simulation.parameters['values']['temperatures'].astext != None
    )

    with sess.Session(bind=op.get_bind()) as session:
        simulations = session.scalars(statement)

        for simulation in simulations:
            parameters = copy.deepcopy(simulation.parameters)

            # Basic safety check
            if not isinstance(parameters, dict):
                continue

            values = parameters.get("values", {})
            if not isinstance(values, dict):
                continue

            # Remove the temperatures field
            if "temperatures" in values:
                values.pop("temperatures")
                parameters["values"] = values
                simulation.parameters = parameters

        session.commit()