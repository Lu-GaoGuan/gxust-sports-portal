#!/bin/sh
set -eu

PROJECT_DIR=${1:-/opt/sports-portal}
BACKUP_DIR=${2:-/opt/sports-portal-backups}
STAMP=$(date +%Y%m%d-%H%M%S)

cd "$PROJECT_DIR"
mkdir -p "$BACKUP_DIR/$STAMP"

set -a
. ./.env.production
set +a

docker compose --env-file .env.production exec -T db \
    mysqldump -u root -p"$DB_ROOT_PASSWORD" --single-transaction --routines --triggers "$DB_NAME" \
    > "$BACKUP_DIR/$STAMP/database.sql"

docker compose --env-file .env.production exec -T web \
    tar czf - -C /app/backend/media . \
    > "$BACKUP_DIR/$STAMP/media.tar.gz"

echo "备份完成：$BACKUP_DIR/$STAMP"
