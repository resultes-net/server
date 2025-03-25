#!/bin/env bash

. venv-wsl/bin/activate

alembic upgrade head --sql > alembic/upgrade.sql

docker-compose.exe up -d
