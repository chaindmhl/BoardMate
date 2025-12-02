#!/bin/bash
# Exit immediately if a command fails
set -e

echo "Starting Django setup..."

echo "MODEL1 contents:"
ls -l /models/model1

echo "MODEL2 contents:"
ls -l /models/model2


# Make migrations for any app changes
python manage.py makemigrations

# Apply database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

echo "Starting Background Worker (Django-Q)..."
python manage.py qcluster &

echo "Starting Gunicorn..."
gunicorn Electronic_exam.wsgi:application --bind 0.0.0.0:9000
