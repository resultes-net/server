"""Add weather data table.

Replaces the `simulation.location` enum column with a foreign key into the new
`weatherdata` table. The former locations are added to that table as shared
weather data (i.e. with `user_id` NULL), keeping their enum names (lower-cased)
as IDs, so that existing simulations can be migrated.

The weather data files themselves are *not* uploaded to the object store by
this migration.

Revision ID: 5768c6a95777
Revises: e2de16a7a23b
Create Date: 2026-09-30 16:49:49.604973

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5768c6a95777'
down_revision: Union[str, None] = 'e2de16a7a23b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_LOCATIONS = [
    'BERLIN', 'BRUSSELS', 'COPENHAGEN', 'MADRID', 'ZURICH', 'ALPINE', 'COLD', 'DRY', 'HOT', 'MEDITERRANEAN',
    'SUBTROPIC', 'TEMPERATE', 'TROPICAL', 'WET',
]

# Only the locations whose weather data the systems code has. No simulations use the dropped ones (Berlin,
# Brussels, Copenhagen, Madrid), otherwise the foreign key below fails.
# (location enum name, name, file name, format)
_SHARED_WEATHER_DATA = [
    ('ZURICH', 'Zurich', 'CH-Zuerich-Kloten-66700.tm2', 'TM2'),
    ('ALPINE', 'Alpine', 'Alpine.csv', 'ISO'),
    ('COLD', 'Cold', 'Cold.csv', 'ISO'),
    ('DRY', 'Dry', 'Dry.csv', 'ISO'),
    ('HOT', 'Hot', 'Hot.csv', 'ISO'),
    ('MEDITERRANEAN', 'Mediterranean', 'Mediterranean.csv', 'ISO'),
    ('SUBTROPIC', 'Subtropic', 'Subtropic.csv', 'ISO'),
    ('TEMPERATE', 'Temperate', 'Temperate.csv', 'ISO'),
    ('TROPICAL', 'Tropical', 'Tropical.csv', 'ISO'),
    ('WET', 'Wet', 'Wet.csv', 'ISO'),
]


def upgrade() -> None:
    sa.Enum('TM2', 'ISO', name='weatherdataformat').create(op.get_bind())
    weather_data_table = op.create_table('weatherdata',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=128), nullable=False),
    sa.Column('file_name', sqlmodel.sql.sqltypes.AutoString(length=1024), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(length=16), nullable=False),
    sa.Column('format', postgresql.ENUM('TM2', 'ISO', name='weatherdataformat', create_type=False), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(length=16), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'name', postgresql_nulls_not_distinct=True)
    )

    op.bulk_insert(
        weather_data_table,
        [
            dict(id=location.lower(), name=name, file_name=file_name, format=format_, user_id=None)
            for location, name, file_name, format_ in _SHARED_WEATHER_DATA
        ],
    )

    op.add_column('simulation', sa.Column('weather_data_id', sqlmodel.sql.sqltypes.AutoString(length=16), nullable=True))
    op.execute("UPDATE simulation SET weather_data_id = lower(location::text)")
    op.alter_column('simulation', 'weather_data_id', nullable=False)
    op.create_foreign_key('simulation_weather_data_id_fkey', 'simulation', 'weatherdata', ['weather_data_id'], ['id'], ondelete='RESTRICT')

    op.drop_column('simulation', 'location')
    sa.Enum(*_LOCATIONS, name='location').drop(op.get_bind())


def downgrade() -> None:
    connection = op.get_bind()

    n_simulations_with_user_uploaded_weather_data = connection.execute(sa.text(
        "SELECT count(*) FROM simulation s JOIN weatherdata w ON s.weather_data_id = w.id WHERE w.user_id IS NOT NULL"
    )).scalar_one()
    if n_simulations_with_user_uploaded_weather_data:
        raise RuntimeError(
            f"Can't downgrade: {n_simulations_with_user_uploaded_weather_data} simulation(s) use user uploaded weather data."
        )

    sa.Enum(*_LOCATIONS, name='location').create(connection)
    op.add_column('simulation', sa.Column('location', postgresql.ENUM(*_LOCATIONS, name='location', create_type=False), autoincrement=False, nullable=True))
    op.execute("UPDATE simulation SET location = upper(weather_data_id)::location")
    op.alter_column('simulation', 'location', nullable=False)

    op.drop_constraint('simulation_weather_data_id_fkey', 'simulation', type_='foreignkey')
    op.drop_column('simulation', 'weather_data_id')
    op.drop_table('weatherdata')
    sa.Enum('TM2', 'ISO', name='weatherdataformat').drop(connection)
