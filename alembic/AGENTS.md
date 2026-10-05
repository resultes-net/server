# Guidance for agents working on migrations

- `env.py` imports all table models (`from sqlmodel_models import *`), so *every* Alembic command fails if a model doesn't
  import. New table models must be exported from `src/sqlmodel_models/__init__.py`, or autogenerate won't see them.
- The connection string comes from `src/config.py` (env vars `DB_HOST_NAME`, `DB_PORT`, ...), not from `alembic.ini`.
- In production, migrations are run by the `docker/migrate` image (`alembic upgrade head`).
- Enum columns are stored by the Python enum member's *name* (e.g. `ZURICH`), not its value. `alembic_postgresql_enum` is
  installed and autogenerates enum type changes (`op.sync_enum_values`).
- Autogenerate only covers the schema. When a change affects existing rows (a new NOT NULL column, replacing a column, seed
  data), hand-write the data migration: add the column as nullable, fill it with `UPDATE`, then set it NOT NULL. Give
  constraints explicit names so the downgrade can drop them. If a downgrade can't preserve data, fail loudly instead.
- After writing a migration, `alembic check` must report "No new upgrade operations detected."

## Testing a migration on a throwaway database
The initial migration (`4b2544451d66`) can't build an empty database: it uses the enum types `simulationstate`,
`location` and `variationstate` with `create_type=False` but never creates them. Create them by hand first (values are in
the initial migration). A recipe that works in WSL with the system's PostgreSQL 16:

```sh
D=<scratch dir>; B=/usr/lib/postgresql/16/bin
$B/initdb -D $D/pg -U postgres --auth=trust -E UTF8
$B/pg_ctl -D $D/pg -o "-p 56543 -k $D -c listen_addresses=localhost" -l $D/pg.log start
psql -h localhost -p 56543 -U postgres -c "create database resultes"
# create the three enum types (see above), then:
DB_PORT=56543 venv/bin/alembic upgrade head
# ... insert sample data at the previous revision, test upgrade/downgrade, then:
$B/pg_ctl -D $D/pg stop -m fast
```

Insert realistic sample data (users, simulations) at the previous revision before testing the new one, and test both
`upgrade` and `downgrade`.
