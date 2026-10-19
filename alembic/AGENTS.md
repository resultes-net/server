# Guidance for agents working on migrations

1. Start every migration with autogenerate (`venv/bin/alembic revision --autogenerate -m "..."`, against a database at
   head, e.g. a throwaway one, see below) and build on its output, rather than writing the migration from scratch. Add by
   hand only what autogenerate doesn't cover (see the data migrations below). For a change that's only in the JSON
   `parameters` column, autogenerate finds nothing: the migration is then hand-written on its empty template.
1. `env.py` imports all table models (`from sqlmodel_models import *`), so *every* Alembic command fails if a model doesn't
   import. New table models must be exported from `src/sqlmodel_models/__init__.py`, or autogenerate won't see them.
1. The connection string comes from `src/config.py` (env vars `DB_HOST_NAME`, `DB_PORT`, ...), not from `alembic.ini`.
1. In production, migrations are run by the `docker/migrate` image (`alembic upgrade head`).
1. Enum columns are stored by the Python enum member's *name* (e.g. `ZURICH`), not its value. `alembic_postgresql_enum` is
   installed and autogenerates enum type changes (`op.sync_enum_values`).
1. Autogenerate only covers the schema. When a change affects existing rows (a new NOT NULL column, replacing a column, seed
   data), hand-write the data migration: add the column as nullable, fill it with `UPDATE`, then set it NOT NULL. Give
   constraints explicit names so the downgrade can drop them. If a downgrade can't preserve data, fail loudly instead.
1. After writing a migration, `alembic check` must report "No new upgrade operations detected."

## Testing a migration on a throwaway database
The initial migration (`4b2544451d66`) can't build an empty database: it uses the enum types `simulationstate`,
`location` and `variationstate` with `create_type=False` but never creates them. Create them by hand first (values are in
the initial migration). A recipe that works in WSL with the system's PostgreSQL 16:

```sh
D=<scratch dir>; B=/usr/lib/postgresql/16/bin
$B/initdb -D $D/pg -U postgres --auth=trust -E UTF8
# TCP only: a Unix socket in a long scratch dir path exceeds Postgres's 107-byte limit, and the server doesn't start.
$B/pg_ctl -D $D/pg -o "-p 56543 -c unix_socket_directories='' -c listen_addresses=localhost" -l $D/pg.log start
psql -h localhost -p 56543 -U postgres -c "create database resultes"
# create the three enum types (see above), then:
DB_PORT=56543 venv/bin/alembic upgrade head
# ... insert sample data at the previous revision, test upgrade/downgrade, then:
$B/pg_ctl -D $D/pg stop -m fast
```

Insert realistic sample data (users, simulations) at the previous revision before testing the new one, and test both
`upgrade` and `downgrade`.
