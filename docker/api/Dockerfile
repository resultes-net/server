FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements/*.linux.txt requirements/

COPY ../../resultes_server resultes_server
COPY ../../pyproject.toml pyproject.toml

RUN python -m pip install --no-cache-dir -r requirements/dev.linux.txt

ENTRYPOINT ["python", "resultes_server/main.py"]
