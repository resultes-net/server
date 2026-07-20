"""Include unit in coll. perf. param A0.

Revision ID: 471ed5924498
Revises: 18f2a7d90699
Create Date: 2026-07-20 15:19:44.795674

"""

import copy
from typing import Sequence, Union

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy.orm.session as sess
import sqlmodel

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "471ed5924498"
down_revision: Union[str, None] = "18f2a7d90699"
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

            performance_coefficients = parameters["values"]["collector_field"][
                "performance_coefficients"
            ]

            a0 = performance_coefficients.pop("a0")
            performance_coefficients["a0_1"] = a0

            simulation.parameters = parameters

        session.commit()


def downgrade() -> None:
    raise NotImplementedError()
