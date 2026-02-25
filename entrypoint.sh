#!/usr/bin/env sh
set -e

echo "Running database migrations..."
/opt/venv/bin/alembic -c /app/alembic.ini upgrade head

echo "Starting application..."
exec /opt/venv/bin/python -m misbot.app
