"""Use hex IDs for shared weather data.

Migration `5768c6a95777` gave the shared weather data the lower-cased names of
the former `Location` enum values as IDs (`zurich`, `alpine`, ...). This
replaces them with hard-coded IDs of the same format as the generated ones of
user uploaded weather data (10 lowercase hex characters), so that IDs are opaque
for all weather data. Simulations are updated accordingly.

Revision ID: 84d20633c464
Revises: 5768c6a95777
Create Date: 2026-10-06 10:41:05.559559

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '84d20633c464'
down_revision: Union[str, None] = '5768c6a95777'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (old ID, new ID)
_IDS = [
    ('zurich', 'bc75a61bfd'),
    ('alpine', 'c8a15e846e'),
    ('cold', '7634132ef1'),
    ('dry', '0875a01ccb'),
    ('hot', '9c92f5554e'),
    ('mediterranean', '48a257e131'),
    ('subtropic', '6c78e63690'),
    ('temperate', '37b95b4de7'),
    ('tropical', '4541d24b4b'),
    ('wet', 'd05b0a7a3a'),
]


def upgrade() -> None:
    _replace_ids({old_id: new_id for old_id, new_id in _IDS})


def downgrade() -> None:
    _replace_ids({new_id: old_id for old_id, new_id in _IDS})


def _replace_ids(new_ids_by_old_id: dict[str, str]) -> None:
    # The foreign key isn't `ON UPDATE CASCADE`, so it's dropped while both tables are updated.
    op.drop_constraint('simulation_weather_data_id_fkey', 'simulation', type_='foreignkey')

    cases = " ".join(f"WHEN '{old_id}' THEN '{new_id}'" for old_id, new_id in new_ids_by_old_id.items())
    old_ids = ", ".join(f"'{old_id}'" for old_id in new_ids_by_old_id)
    op.execute(f"UPDATE weatherdata SET id = CASE id {cases} END WHERE id IN ({old_ids}) AND user_id IS NULL")
    op.execute(
        f"UPDATE simulation SET weather_data_id = CASE weather_data_id {cases} END"
        f" WHERE weather_data_id IN ({old_ids})"
    )

    op.create_foreign_key(
        'simulation_weather_data_id_fkey', 'simulation', 'weatherdata', ['weather_data_id'], ['id'], ondelete='RESTRICT'
    )
