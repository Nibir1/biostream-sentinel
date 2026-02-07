# Base Image: Official Python 3.11 Slim (Debian-based)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system build dependencies (required for some Python packages)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 1. Copy ALL application code first
# (Crucial: "pip install ." needs the source code to build the package wheel)
COPY . .

# 2. Install the project and dependencies
RUN pip install --no-cache-dir .

# Run the application
# Host 0.0.0.0 is critical for Docker networking
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]