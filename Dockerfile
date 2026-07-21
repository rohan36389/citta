# ==========================================
# CittaAI Backend Production Dockerfile
# ==========================================
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    ENVIRONMENT=production \
    DEBUG=false \
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

# Build offline vector database during Docker container build phase (Content-Hash Gated)
RUN python /app/backend/scripts/build_vector_db.py

# Verify build-time vector database artifact & print chunk count
RUN ls -lh /app/backend/vector_store.db && \
    python -c "import sqlite3; conn=sqlite3.connect('/app/backend/vector_store.db'); print('Build-time DB Chunk Count:', conn.execute('select count(*) from chunks').fetchone()[0]); conn.close()"

# Set working directory to backend
WORKDIR /app/backend

# Expose default backend port
EXPOSE 8000

# Start Uvicorn ASGI server respecting Railway's PORT environment variable
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]
