#!/bin/bash
# Exit immediately if a command fails
set -e

echo "Starting Django setup..."

echo "Listing model1 contents:"
ls -l /app/model1
echo "Listing model2 contents:"
ls -l /app/model2

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
