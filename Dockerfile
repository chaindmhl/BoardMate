FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV DJANGO_SETTINGS_MODULE=Electronic_exam.settings

WORKDIR /app

RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 unzip curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install all Python packages
COPY requirements.txt /app/
ARG PYTHON_CACHEBUST=1
RUN echo "Cache bust: $PYTHON_CACHEBUST" \
    && pip install --no-cache-dir -r requirements.txt


# Copy project files
COPY . /app/

# # Download YOLO models
# RUN mkdir -p /app/model1 /app/model2 \
#     && curl -L -o model1.zip https://github.com/chaindmhl/BoardMate/releases/download/v1.0/model1.zip \
#     && unzip -j model1.zip -d model1 && rm model1.zip \
#     && curl -L -o model2.zip https://github.com/chaindmhl/BoardMate/releases/download/v1.0/model2.zip \
#     && unzip -j model2.zip -d model2 && rm model2.zip

# Download YOLO models
RUN mkdir -p /app/model1 /app/model2 \
    && curl -L -o model1.zip https://github.com/chaindmhl/BoardMate/releases/download/v1.0/model1.zip \
    && unzip model1.zip -d /app/model1 && rm model1.zip \
    && curl -L -o model2.zip https://github.com/chaindmhl/BoardMate/releases/download/v1.0/model2.zip \
    && unzip model2.zip -d /app/model2 && rm model2.zip

# Create directories
RUN mkdir -p /app/staticfiles /app/media

# Entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 9000
CMD ["/app/entrypoint.sh"]
