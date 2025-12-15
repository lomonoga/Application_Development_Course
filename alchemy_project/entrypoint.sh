#!/bin/bash

set -e

echo "Waiting for PostgreSQL at ${DB_HOST:-postgres}:${DB_PORT:-5432}..."
while ! nc -z ${DB_HOST:-postgres} ${DB_PORT:-5432}; do
    sleep 0.5
    echo "Still waiting for database..."
done
echo "Database is ready!"

if [ -f "alembic.ini" ]; then
    echo "Applying Alembic migrations..."
    alembic upgrade head
else
    echo "No alembic.ini found, skipping migrations"
fi

echo "Starting application..."
exec "$@"