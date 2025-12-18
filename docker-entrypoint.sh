#!/bin/bash

set -e

if [ "$USE_POSTGRES" = "True" ]; then
  echo "Waiting for PostgreSQL..."
  until pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
  done
  echo "PostgreSQL started"
fi

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating sample data..."
python setup.py <<EOF
y
EOF

exec "$@"
