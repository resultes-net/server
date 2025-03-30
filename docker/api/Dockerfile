FROM python:3.12-slim-bookworm AS pip-dependencies

WORKDIR /app

COPY requirements/*.txt requirements/

RUN python -m pip install --no-cache-dir -r requirements/dev-3rd-party.txt

FROM pip-dependencies

COPY src/resultes_server src/resultes_server
COPY pyproject.toml pyproject.toml

RUN python -m pip install --no-cache-dir .

COPY alembic alembic
COPY alembic.ini alembic.ini


ENTRYPOINT ["python", "src/resultes_server/main.py"]
