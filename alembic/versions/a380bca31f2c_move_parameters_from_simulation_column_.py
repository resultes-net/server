"""Move parameters from simulation column into own table..

Revision ID: a380bca31f2c
Revises: 99d4ccb51f02
Create Date: 2026-07-23 16:38:49.858333

"""

import copy
from typing import Sequence, Union

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy.orm.session as sess
import sqlmodel
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a380bca31f2c"
down_revision: Union[str, None] = "99d4ccb51f02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

Base = orm.declarative_base()


class Simulation(Base):
    __tablename__ = "simulation"

    id = sa.Column(sa.String, primary_key=True)
    parameters = sa.Column(postgresql.JSONB, nullable=False)


class Parameters(Base):
    __tablename__ = "parameters"

    simulation_id = sa.Column(
        sa.String, sa.ForeignKey("simulation.id"), primary_key=True
    )
    parameters = sa.Column(postgresql.JSONB, nullable=False)


def upgrade() -> None:
    op.create_table(Parameters.__table__)

    statement = sa.select(Simulation.id, Simulation.parameters)

    with sess.Session(bind=op.get_bind()) as session:
        simulation_ids_and_parameter = session.execute(statement)

        for simulation_id, old_parameters in simulation_ids_and_parameter:
            parameters = copy.deepcopy(old_parameters)

            old_waste_heat_recovery_source = parameters["values"][
                "waste_heat_recovery_source"
            ]
            mass_flow_rates_kg_per_h, temperatures_deg_C = zip(
                *(
                    (v["mass_flow_rate_kg_per_h"], v["temperature_deg_C"])
                    for v in old_waste_heat_recovery_source["hourly_values"]
                )
            )

            new_waste_heat_recovery_source = {
                "name": old_waste_heat_recovery_source["name"],
                "mass_flow_rates_kg_per_h": mass_flow_rates_kg_per_h,
                "temperatures_deg_C": temperatures_deg_C,
            }

            parameters["values"][
                "waste_heat_recovery_source"
            ] = new_waste_heat_recovery_source

            sa.insert(Parameters).values(
                (
                    Parameters.simulation_id == simulation_id,
                    Parameters.parameters == parameters,
                ),
            )

            session.commit()

    op.drop_column("simulation", "parameters")


def downgrade() -> None:
    raise NotImplementedError()
