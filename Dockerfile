# Base image
FROM python:3.9

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV DJANGO_SETTINGS_MODULE=Electronic_exam.settings

# Set working directory
WORKDIR /app

# Install system dependencies first
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 unzip curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . /app/

# Download YOLO models
RUN mkdir -p /app/model1 /app/model2 \
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

# Copy entrypoint script and make it executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Run entrypoint
CMD ["/app/entrypoint.sh"]
