ENV PIP_ARGS=" --no-cache-dir --root-user-action"
ENV PIP_INSTALL="python -m uv pip install $PIP_ARGS"

FROM python:3.12-slim-bookworm AS pip-dependencies

WORKDIR /app

COPY requirements/run-3rd-party.txt requirements/

RUN python -m pip install $PIP_ARGS --upgrade wheel uv pip
RUN $PIP_INSTALL -r requirements/run-3rd-party.txt

FROM pip-dependencies

COPY src/resultes_server src/resultes_server
COPY pyproject.toml ./

RUN $PIP_INSTALL .

COPY alembic alembic
COPY alembic.ini ./


ENTRYPOINT ["python", "src/resultes_server/main.py"]
