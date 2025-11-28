# Use the official Python image as a base image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Add this line to include /app in Python’s module search path
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0


# Copy the rest of the application code
COPY . /app/

# Create static and media directories (important)
RUN mkdir -p /app/staticfiles /app/media

# Optional: collect static files if you use them
RUN python manage.py collectstatic --noinput || true

# Expose the desired port
EXPOSE 9000

# Run the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:9000"]
