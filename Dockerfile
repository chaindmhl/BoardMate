# Base image
FROM python:3.9

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV DJANGO_SETTINGS_MODULE=Electronic_exam.settings

# Working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 unzip curl \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Cache-busting arguments
# -----------------------------
# Change these to force reinstall of Python packages or models
ARG PYTHON_CACHEBUST=1
ARG MODEL_CACHEBUST=1

# Copy requirements first and install Python packages
COPY requirements.txt /app/
RUN echo "Cache bust: $PYTHON_CACHEBUST" \
    && pip install --no-cache-dir -r requirements.txt

# Ensure django-q is installed (optional, safe)
RUN pip install --no-cache-dir --upgrade django-q

# Copy project code
COPY . /app/

# Download YOLO models (cache-busted)
RUN echo "Model cache bust: $MODEL_CACHEBUST" \
    && mkdir -p /app/model1 /app/model2 \
    && curl -L -o model1.zip https://github.com/chaindmhl/BoardMate/releases/download/v1.0/model1.zip \
    && unzip -j model1.zip -d model1 \
    && rm model1.zip \
    && curl -L -o model2.zip https://github.com/chaindmhl/BoardMate/releases/download/v1.0/model2.zip \
    && unzip -j model2.zip -d model2 \
    && rm model2.zip

# Create static and media directories
RUN mkdir -p /app/staticfiles /app/media

# Expose port
EXPOSE 9000

# Copy entrypoint script and make executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Run entrypoint
CMD ["/app/entrypoint.sh"]
