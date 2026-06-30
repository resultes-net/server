"""Add location to simulation.

Revision ID: a57548945a07
Revises: 13ea35d677aa
Create Date: 2026-06-30 15:18:28.767982

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a57548945a07'
down_revision: Union[str, None] = '13ea35d677aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sa.Enum('BERLIN', 'BRUSSELS', 'COPENHAGEN', 'MADRID', 'ZURICH', name='location').create(op.get_bind())
    
    op.add_column('simulation', sa.Column('location', postgresql.ENUM(name='location'), nullable=True))

    simulation = sa.table('simulation', sa.column('location'))
    op.execute(simulation.update().values(location='ZURICH'))

    op.alter_column('simulation', 'location', nullable=False)



def downgrade() -> None:
    simulation = sa.table('simulation', sa.column('location'), sa.column('id'))
    variation = sa.table('variation', sa.column('simulation_id'))

    simulation_ids_to_delete = sa.select(simulation.c.id).where(simulation.c.location != 'ZURICH')

    op.execute(variation.delete().where(variation.c.simulation_id.in_(simulation_ids_to_delete)))
    op.execute(simulation.delete().where(simulation.c.id.in_(simulation_ids_to_delete)))

    op.drop_column('simulation', 'location')
    sa.Enum('BERLIN', 'BRUSSELS', 'COPENHAGEN', 'MADRID', 'ZURICH', name='location').drop(op.get_bind())
