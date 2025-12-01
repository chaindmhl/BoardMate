#!/bin/bash
# entrypoint.sh

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
exec gunicorn --bind 0.0.0.0:9000 Electronic_exam.wsgi:application
