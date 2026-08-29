#!/bin/sh
set -eu

PROJECT_DIR=${1:-/opt/sports-portal}
cd "$PROJECT_DIR"

if [ ! -f .env.production ]; then
    echo "缺少 .env.production。"
    exit 1
fi

docker compose --env-file .env.production build
docker compose --env-file .env.production up -d
docker compose --env-file .env.production ps
