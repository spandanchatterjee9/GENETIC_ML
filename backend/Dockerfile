# Use official Python 3.11 slim image as the base
FROM python:3.11-slim

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker's layer caching
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
# Note: Virtual environments, local outputs, caches, and git files are excluded via .dockerignore
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Run the application using Uvicorn for production
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT} --workers 4"]
