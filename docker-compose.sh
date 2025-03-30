#!/bin/env sh

DOCKER_BAKE=true docker-compose.exe build

docker-compose.exe up -d

sleep 5

docker exec resultes-server-api-1 alembic upgrade head
