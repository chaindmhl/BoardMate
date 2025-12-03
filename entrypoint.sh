#!/bin/bash
set -e

# 1. Apply migrations
echo "Applying migrations..."
python manage.py migrate

# 2. Collect static files (optional)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# 3. Start Django Q cluster in the background
echo "Starting Django Q cluster..."
python manage.py qcluster &

# 4. Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn Electronic_exam.wsgi:application \
    --bind 0.0.0.0:9000 \
    --workers 3
