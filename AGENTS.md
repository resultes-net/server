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
