# File: Dockerfile
# Purpose: Defines the environment and instructions for building the application's Docker image.

# --- Stage 1: Base Image ---
# Use a specific version of the official Python slim image for reproducibility and security.
# 'bookworm' is the stable Debian release corresponding to Python 3.11, ensuring a lean yet complete OS.
FROM python:3.12-slim

# --- Metadata ---
LABEL maintainer="CodeNavigator AI"
LABEL description="Docker image for the Automated Financial Analysis System."

# --- Environment Variables ---
# Prevents Python from buffering stdout and stderr, ensuring logs appear in real-time.
ENV PYTHONUNBUFFERED=1
# Adds the 'src' directory to Python's path, allowing for clean absolute imports.
ENV PYTHONPATH=/app/src
# Sets the working directory for all subsequent commands.
WORKDIR /app

# --- System Dependencies ---
# Update package lists and install essential build tools and libraries required by Python packages
# like pandas, lxml, and Pillow (a dependency of pdfplumber, though not used, it's a common need).
# This ensures native extensions can be compiled successfully.
# We clean up apt cache files in the same layer to reduce image size.
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --- Python Dependencies ---
# Copy only the requirements file first to leverage Docker's layer caching.
# This layer will only be rebuilt if requirements.txt changes, not on every code change.
COPY requirements.txt .

# Upgrade pip and install the Python dependencies into the system's Python environment.
# --no-cache-dir reduces the image size by not storing the pip cache.
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# --- Application Code ---
# Copy the rest of the application source code into the container.
COPY ./src /app/src
COPY main.py .

# --- Final Configuration ---
# Expose the port that a future web interface (e.g., FastAPI, Flask) might use.
EXPOSE 8000

# Set the default command to run when the container starts.
# This provides a sensible default but can be easily overridden in docker-compose.yml or via the command line.
CMD ["python3", "main.py", "--ticker", "AAPL"]
