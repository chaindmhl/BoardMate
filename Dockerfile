FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV DJANGO_SETTINGS_MODULE=Electronic_exam.settings

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 unzip curl \
    && rm -rf /var/lib/apt/lists/*

# Build-time cache busting
ARG PYTHON_CACHEBUST=1
ARG MODEL_CACHEBUST=1

# Copy and install dependencies
COPY requirements.txt /app/
RUN echo "Cache bust: $PYTHON_CACHEBUST" && pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . /app/

# Download YOLO models
RUN echo "Model cache bust: $MODEL_CACHEBUST" \
    && mkdir -p /app/model1 /app/model2 \
    && curl -L -o model1.zip https://github.com/chaindmhl/BoardMate/releases/download/v1.0/model1.zip \
    && unzip -j model1.zip -d model1 && rm model1.zip \
    && curl -L -o model2.zip https://github.com/chaindmhl/BoardMate/releases/download/v1.0/model2.zip \
    && unzip -j model2.zip -d model2 && rm model2.zip

RUN mkdir -p /app/staticfiles /app/media

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 9000

CMD ["/app/entrypoint.sh"]
