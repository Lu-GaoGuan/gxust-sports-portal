FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends default-libmysqlclient-dev build-essential pkg-config curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt backend/requirements-production.txt /app/backend/
RUN python -m pip install --upgrade pip \
    && python -m pip install -r /app/backend/requirements-production.txt

COPY backend /app/backend
COPY deploy/scripts/backend-entrypoint.sh /app/deploy/backend-entrypoint.sh

# Confirmed public derivatives are staged separately because /app/backend/media
# is mounted as a persistent volume in production.
RUN mkdir -p /app/seed_media \
    && if [ -d /app/backend/media ]; then cp -a /app/backend/media/. /app/seed_media/; fi \
    && chmod +x /app/deploy/backend-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/deploy/backend-entrypoint.sh"]
CMD ["/bin/sh", "-c", "exec gunicorn config.wsgi:application --chdir /app/backend --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-3} --threads ${GUNICORN_THREADS:-2} --timeout ${GUNICORN_TIMEOUT:-60} --access-logfile - --error-logfile -"]
