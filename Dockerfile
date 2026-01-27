# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POPPLER_PATH=/usr/bin

# Set work directory
WORKDIR /app

# Install system dependencies (Poppler, Tesseract, Postgres libs)
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
RUN pip install uv

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies using uv (merging both files)
RUN uv pip install --system -r requirements.txt

# Copy the application code
COPY sentry_app/ ./sentry_app/

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "sentry_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
