FROM python:3.12-slim-bookworm AS pip-dependencies

WORKDIR /app

COPY docker-utils docker-utils
COPY requirements/run-3rd-party.txt requirements/

RUN docker-utils/pip-install.sh --upgrade wheel uv pip
RUN docker-utils/uv-pip-install.sh -r requirements/run-3rd-party.txt

FROM pip-dependencies

COPY src/resultes_server src/resultes_server
COPY pyproject.toml ./

RUN docker-utils/uv-pip-install.sh .

COPY alembic alembic
COPY alembic.ini ./


ENTRYPOINT ["python", "src/resultes_server/main.py"]
