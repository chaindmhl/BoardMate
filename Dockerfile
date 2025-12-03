FROM python:3.9

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV DJANGO_SETTINGS_MODULE=Electronic_exam.settings

# Working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
ARG PYTHON_CACHEBUST=1
RUN echo "Cache bust: $PYTHON_CACHEBUST" \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Create static/media directories
RUN mkdir -p /app/staticfiles /app/media

# Entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 9000
CMD ["/app/entrypoint.sh"]
