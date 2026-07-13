#!/usr/bin/env sh
set -e

echo "[misbot entrypoint.sh] EXECUTE_MIGRATIONS=${EXECUTE_MIGRATIONS:-false}"

if [ "${EXECUTE_MIGRATIONS:-false}" = "true" ]; then
    echo "[misbot entrypoint.sh] Performing database migrations"
    /opt/venv/bin/alembic -c /app/alembic.ini upgrade head
fi

if [ "$#" -eq 0 ]; then
    echo "[misbot entrypoint.sh] No command specified"
    exit 1
fi

exec "$@"
