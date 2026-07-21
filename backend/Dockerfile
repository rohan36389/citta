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
    VECTOR_DB_PATH=/app/vector_store.db \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Build offline vector database during Docker container build phase (Content-Hash Gated)
RUN python scripts/build_vector_db.py

# Verify build-time vector database artifact & print chunk count
RUN ls -lh vector_store.db && \
    python -c "import sqlite3; conn=sqlite3.connect('vector_store.db'); print('Build-time DB Chunk Count:', conn.execute('select count(*) from chunks').fetchone()[0]); conn.close()"

EXPOSE 8000

# Start Uvicorn ASGI server respecting Railway's PORT environment variable
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]
