"""Add A3-5 collector performance parameters.

Revision ID: 18f2a7d90699
Revises: 428997de973c
Create Date: 2026-07-20 11:23:55.923814

"""

import copy
from typing import Sequence, Union

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy.orm.session as sess
import sqlmodel

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "18f2a7d90699"
down_revision: Union[str, None] = "428997de973c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PERFORMANCE_COEFFICIENTS = {
    "a0": 0.737,
    "a1_kW_per_m2_per_K": 0.0005,
    "a2_kW_per_m2_per_K2": 6e-06,
    "a3_kJ_per_m3_per_K": 0,
    "a4_1": 0,
    "a5_kJ_per_m2_per_K": 15.32,
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

            collector_field = parameters["values"]["collector_field"]

            # We're overwriting existing performance coefficients here, but at this stage of development
            # I can guarantee that those params were ignored and the ones that were actually used in the
            # simulation were the ones we're overwriting the ignored ones here.
            collector_field["performance_coefficients"] = PERFORMANCE_COEFFICIENTS

            simulation.parameters = parameters

        session.commit()


def downgrade() -> None:
    raise NotImplementedError()
