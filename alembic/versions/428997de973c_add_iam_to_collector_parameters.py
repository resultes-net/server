"""Add IAM to collector parameters.

Revision ID: 428997de973c
Revises: 992dcc98dec6
Create Date: 2026-07-15 16:50:06.579697

"""

import json
import copy
from typing import Sequence, Union

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy.orm.session as sess
import sqlmodel

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "428997de973c"
down_revision: Union[str, None] = "992dcc98dec6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


IAM_DATA = json.loads(r"""{
        "name": "<default>",
        "transversal_angles_degC": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0],
        "longitudinal_angles_degC": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0],
        "values": [
            1,
            1,
            0.99,
            0.98,
            0.95,
            0.88,
            0.72,
            0.36,
            0,
            1,
            1,
            0.99,
            0.98,
            0.95,
            0.88,
            0.72,
            0.36,
            0,
            0.99,
            0.99,
            0.9801,
            0.9702,
            0.9405,
            0.8712,
            0.7128,
            0.3564,
            0,
            0.98,
            0.98,
            0.9702,
            0.9604,
            0.931,
            0.8624,
            0.7056,
            0.3528,
            0,
            0.95,
            0.95,
            0.9405,
            0.931,
            0.9025,
            0.836,
            0.684,
            0.342,
            0,
            0.88,
            0.88,
            0.8712,
            0.8624,
            0.836,
            0.7744,
            0.6336,
            0.3168,
            0,
            0.72,
            0.72,
            0.7128,
            0.7056,
            0.684,
            0.6336,
            0.5184,
            0.2592,
            0,
            0.36,
            0.36,
            0.3564,
            0.3528,
            0.342,
            0.3168,
            0.2592,
            0.1296,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0]
    }                       
""")


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

            collector_field["iam"] = IAM_DATA

            simulation.parameters = parameters

        session.commit()


def downgrade() -> None:
    raise NotImplementedError()
