#!/bin/sh
set -eu

PROJECT_DIR=${1:-/opt/sports-portal}
cd "$PROJECT_DIR"

if [ ! -f .env.production ]; then
    echo "缺少 $PROJECT_DIR/.env.production，请先复制并填写 .env.production.example。"
    exit 1
fi

docker compose --env-file .env.production config >/dev/null
docker compose --env-file .env.production build
docker compose --env-file .env.production up -d
docker compose --env-file .env.production ps

echo "等待服务启动后检查：http://服务器公网IP/api/health/"
echo "创建管理员：docker compose --env-file .env.production exec web python manage.py createsuperuser"
