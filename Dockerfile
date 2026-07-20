# ==========================================
# CittaAI Backend Production Dockerfile
# ==========================================
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    PYTHONPATH=/app/backend

WORKDIR /app

# Install system dependencies required for C extensions & runtime utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements first to optimize Docker layer caching
COPY backend/requirements.txt /app/backend/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend source code
COPY backend/ /app/backend/

# Copy frontend content asset if existing
COPY frontend/src/data/content.js /app/frontend/src/data/content.js

# Set working directory to backend
WORKDIR /app/backend

# Expose default backend port
EXPOSE 8000

# Start Uvicorn ASGI server respecting Railway's PORT environment variable
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]
