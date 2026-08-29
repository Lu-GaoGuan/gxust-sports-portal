#!/bin/sh
set -eu

echo "Waiting for database..."
python - <<'PY'
import os
import time

if os.getenv("DB_ENGINE", "sqlite").lower() != "mysql":
    raise SystemExit(0)

import MySQLdb

for attempt in range(60):
    try:
        connection = MySQLdb.connect(
            host=os.getenv("DB_HOST", "db"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.environ["DB_USER"],
            passwd=os.environ["DB_PASSWORD"],
            db=os.environ["DB_NAME"],
            charset="utf8mb4",
        )
        connection.close()
        break
    except Exception as error:
        if attempt == 59:
            raise
        print(f"Database is not ready ({error}); retrying...")
        time.sleep(2)
PY

mkdir -p /app/backend/media /app/backend/staticfiles
if [ -d /app/seed_media ]; then
    cp -an /app/seed_media/. /app/backend/media/ 2>/dev/null || true
fi

python /app/backend/manage.py migrate --noinput
python /app/backend/manage.py collectstatic --noinput

if [ "${SEED_INITIAL_CONTENT:-false}" = "true" ]; then
    NEEDS_SEED=$(python /app/backend/manage.py shell -c "from portal.models import DepartmentProfile; print('yes' if not DepartmentProfile.objects.exists() else 'no')" | tail -n 1)
    if [ "$NEEDS_SEED" = "yes" ]; then
        python /app/backend/manage.py seed_confirmed_content
    else
        echo "Initial content already exists; skipping seed."
    fi
fi

exec "$@"
