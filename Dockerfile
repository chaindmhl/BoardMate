FROM python:3.9

# Environment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="${PYTHONPATH}:/app"

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0

# Copy code
COPY . /app/

# Create static and media directories
RUN mkdir -p /app/staticfiles /app/media

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 9000

# Use WhiteNoise for static files (recommended)
ENV DJANGO_SETTINGS_MODULE=Electronic_exam.settings

CMD ["gunicorn", "--bind", "0.0.0.0:9000", "Electronic_exam.wsgi:application"]


