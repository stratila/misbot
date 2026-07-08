#!/usr/bin/env sh
set -e

if [ "$#" -gt 0 ]; then
  echo "Executing override command..."
  exec "$@"
fi

echo "Running database migrations..."
/opt/venv/bin/alembic -c /app/alembic.ini upgrade head

echo "Starting application..."
exec /opt/venv/bin/python -m misbot.app
