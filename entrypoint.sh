#!/bin/bash
set -e

if [ -f "/app/.env" ]; then
    export $(grep -v '^#' /app/.env | xargs)
fi

python manage.py makemigrations app --noinput
python manage.py migrate --noinput

python manage.py collectstatic --noinput

exec gunicorn QuartzAgency.wsgi:application --bind 0.0.0.0:8000 --workers 3
