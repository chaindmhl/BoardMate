#!/bin/bash
# Exit immediately if a command fails
set -e

echo "Starting Django setup..."

# Make migrations for any app changes
python manage.py makemigrations

# Apply database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Optionally, run background tasks (Django-Q example)
# python manage.py qcluster &

echo "Starting Gunicorn..."
gunicorn Electronic_exam.wsgi:application --bind 0.0.0.0:9000
