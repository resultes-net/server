#!/bin/env sh

DOCKER_BAKE=true docker-compose.exe build

docker-compose.exe up -d

sleep 5

docker exec -i resultes-server-api-1 bash <<EOF
alembic upgrade head
EOF
