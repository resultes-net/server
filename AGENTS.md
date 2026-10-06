# Guidance for agents working on `server`

For the overall ResulTES architecture, dependency management and deployment, read the org-wide guide first:
https://github.com/resultes-net/issues/blob/main/AGENTS.md. This file only adds what's specific to this repo.

## Layout
- `src/external_server.py`: FastAPI app exposed to the web (authenticated). Endpoint logic lives in `src/external/*.py`.
- `src/internal_server.py`: FastAPI app only reachable inside the cluster (unauthenticated), used by the scheduler.
- `src/sqlmodel_models/`: table models. They usually inherit from the corresponding `pydantic-models` model and add
  database-only fields (foreign keys, relationships). A field that SQLModel can't map to a column (e.g. a union of an enum
  and a model) must not be on a base class that a table model inherits from.
- `alembic/`: migrations, see `alembic/AGENTS.md`.
- `scripts/export_openapi_json.py`: writes the OpenAPI schemas of both apps into the `openapi-schema` submodule.
- Git submodules: `pydantic-models`, `openapi-schema`, `openstack-utils`, `src/database_utils`, `dev-utils`,
  `docker-utils`. Changes to a submodule need a commit *inside* the submodule and then one in `server` that records the new
  submodule commit.

## Environment
- Python 3.12, venv in `venv/`. Code is imported relative to `src/` (e.g. `import sqlmodel_models.user`).
- `src/config.py` reads the database settings from `DB_HOST_NAME`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`. The database name is
  always `resultes`.
- The external server needs Swift credentials (`config/secrets/swift-operator-clouds.yaml`) at startup; the internal server
  doesn't. To run the internal server locally against some database:
  `cd src && DB_PORT=<port> ../venv/bin/uvicorn internal_server:app --port 8000`.

## Tests
- `pytest.ini` sets `python_files = *.py`: tests live *next to the code* in regular modules (functions named `test_*`), not
  only in `test_*.py` files. `norecursedirs` excludes `alembic`, `scripts`, etc., since importing e.g. `alembic/env.py` outside
  of Alembic fails.
- Run with `venv/bin/python -m pytest` from the repo root.

## Type checking
- The code is written for strict Pylance/pyright. `mypy --strict` reports some errors that are already in the code, e.g.
  `Missing named argument "id"` when constructing table models whose `id` has a default factory (`_dbh.ID_FIELD`), and
  `Name "swift" is not defined` in `external_server.py` (it's a global set in the lifespan). Don't "fix" these in passing.

## Conventions and pitfalls
- Imports are aliased with a leading underscore (`import sqlmodel as _sqlm`); follow that.
- IDs are `secrets.token_hex(nbytes=5)`, i.e. 10 lowercase hex characters (`database_utils.helpers.id_default_factory`).
- `database_utils.helpers.create_id_field` marks a column as nullable only if *no* default is given. For a nullable foreign
  key with default `None`, use `sqlmodel.Field(default=None, foreign_key=..., nullable=True)` directly.
- Sessions are created with `expire_on_commit=False`, but a `rollback()` still expires all loaded objects. Accessing their
  attributes afterwards triggers synchronous IO and fails with `MissingGreenlet` in async code.
- `pydantic.Base64Str` is already *decoded* after validation; don't `b64decode` it again.
- Pydantic models aren't mappings: `Model(**other_model)` raises `TypeError`. Use `**other_model.model_dump(...)`.
- API changes affect other repos: after changing endpoints or `pydantic-models`, export the OpenAPI schema (see above),
  and check the scheduler, which parses internal server responses with its *own* `pydantic-models` checkout.

## Weather data
- Table `weatherdata`: rows with `user_id` NULL are shared (the former `Location` enum values, added by migration
  `5768c6a95777`; migration `84d20633c464` gave them hard-coded IDs of the same format as generated ones, e.g. Zurich
  `bc75a61bfd`, Alpine `c8a15e846e`); other rows are user uploads. Names are unique per user including the
  shared "user" (`UNIQUE NULLS NOT DISTINCT (user_id, name)`).
- `simulation.weather_data_id` references it with `ON DELETE RESTRICT`.
- Files live in Swift as zips of `data.<tm2|csv>` and a `README.md` with the name etc.
  (`external.weather_data.write_zip_file`; runner jobs extract them into a directory `selected_weather`), so that users who download a project know which weather data it uses. Shared ones are in container `resultes-static`
  (next to the systems code), path `weather-data/<id>.zip`; uploaded ones in container `resultes-user-data`, path
  `<user_id>/weather-data/<id>.zip`. Paths and file names are computed only in `resultes_pydantic_models.weather_data`
  (`get_object_storage_{input,output}_file_path`, `DIR_NAME`, `get_data_file_name`, `README_FILE_NAME`), so that the scheduler and
  the systems code agree (the scheduler gets the owner from the internal `GET /weather-data/{id}`). The path uses the
  ID, not the name, so names are display-only (any characters, 1-128 long) and renaming doesn't touch the object store
  (the readme keeps the name at upload time).
- Queries for weather data a user may *use* must filter `user_id IS NULL OR user_id = :user`
  (`external.weather_data._create_accessible_by_query`); changes/deletes must only allow the user's own rows.
- Uploads are TM2 (TMY2) files. `external.weather_data.fix_up_and_validate_tm2_contents` fixes up Meteonorm quirks (6-digit
  station numbers, empty state, `99999999?0` present weather field) *without moving any field*, validates with
  `pvlib.iotools.read_tmy2` and requires exactly 8760 data lines. The fixed-up contents are what gets uploaded. TRNSYS
  reads unfixed files too; the fix-ups are needed only because `pvlib` is strict (the systems code reads TM2 with `pvlib`
  as well).
- The shared weather data zips are *not* uploaded by the server or a migration, but by hand. Zurich's TM2 must be fixed
  up as above before uploading.
- Sample TM2 files: `/mnt/c/TRNSYS18/Weather/**/*.tm2` (TRNSYS install on the Windows host, when working in WSL).
