FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements/*.txt requirements/

COPY src/resultes_server src/resultes_server
COPY pyproject.toml pyproject.toml

COPY alembic alembic
COPY alembic.ini alembic.ini

RUN python -m pip install --no-cache-dir -r requirements/dev.txt

ENTRYPOINT ["python", "src/resultes_server/main.py"]
