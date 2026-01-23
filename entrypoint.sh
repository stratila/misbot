#!/usr/bin/env sh
set -e

echo "Running database migrations..."
/app/.venv/bin/alembic -c /app/alembic.ini  upgrade head

echo "Starting application..."
exec /app/.venv/bin/python -m misbot.app
