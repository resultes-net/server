"""Lift (actually) duplicate system type from parameters to simulation..

Revision ID: c696ad9c570c
Revises: 91be872c85d0
Create Date: 2026-07-22 15:30:04.942771

"""

import copy
from typing import Sequence, Union

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy.orm.session as sess
import sqlmodel

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c696ad9c570c"
down_revision: Union[str, None] = "91be872c85d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


Base = orm.declarative_base()


class Simulation(Base):
    __tablename__ = "simulation"

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    type = sa.Column(sa.Enum)
    parameters = sa.Column(sa.JSON)


def upgrade() -> None:
    type_enum = sa.Enum("TTES", "PTES", "BTES", name="type", create_type=False)

    type_enum.create(op.get_bind())

    op.add_column(
        "simulation",
        sa.Column(
            "type",
            type_enum,
            nullable=True,
        ),
    )

    with sess.Session(bind=op.get_bind()) as session:
        source_value = sa.func.cast(
            sa.func.upper(Simulation.parameters["values"]["type"].as_string()),
            type_enum,
        )

        statement = sa.update(Simulation).values(type=source_value)

        session.execute(statement)

        session.commit()

    op.alter_column("simulation", "type", nullable=False)


def downgrade() -> None:
    raise NotImplementedError()
