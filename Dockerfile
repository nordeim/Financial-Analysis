# syntax=docker/dockerfile:1

FROM python:3.12-slim

WORKDIR /app

# System dependencies for pandas, lxml, pdfplumber, etc.
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for layer caching
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories for logs, reports, config, data
RUN mkdir -p /app/logs /app/reports /app/config /app/data /app/templates

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Expose a port for future API/web interface
EXPOSE 8000

# Default command (overrideable in docker-compose)
CMD ["python3", "src/main.py", "AAPL", "--format", "both"]
