FROM python:3.9

# Environment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV DJANGO_SETTINGS_MODULE=Electronic_exam.settings

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install system dependencies
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 unzip curl

# Download YOLO models from GitHub releases
RUN curl -L -o model1.zip https://github.com/chaindmhl/BoardMate/releases/download/v1.0/model1.zip \
    && unzip model1.zip -d model1 \
    && rm model1.zip

RUN curl -L -o model2.zip https://github.com/chaindmhl/BoardMate/releases/download/v1.0/model2.zip \
    && unzip model2.zip -d model2 \
    && rm model2.zip

# Copy project code
COPY . /app/

# Create static and media directories
RUN mkdir -p /app/staticfiles /app/media

# Collect static files at build (optional)
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 9000

# Use entrypoint script to run migrations + start server
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
CMD ["/app/entrypoint.sh"]
