#!/bin/bash
set -e

# 0. Optional: print Python & Django info for debugging
echo "Python version: $(python --version)"
echo "Django version: $(python -m django --version)"

# 1. Make migrations (auto-generate migration files for any model changes)
echo "Making migrations..."
python manage.py makemigrations

# 2. Apply migrations (create/alter DB tables)
echo "Applying migrations..."
python manage.py migrate

# 3. Collect static files (optional)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# 4. Start Django Q cluster in the background
echo "Starting Django Q cluster..."
python manage.py qcluster &

# 5. Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn Electronic_exam.wsgi:application \
    --bind 0.0.0.0:9000 \
    --workers 3

