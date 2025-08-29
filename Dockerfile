# Production Dockerfile for Railway deployment
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY Requirements.txt .
RUN pip install --no-cache-dir -r Requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY Style/ ./Style/
COPY pages/ ./pages/
COPY scrapers/ ./scrapers/
COPY main_app.py ./

# Copy data files (FAISS vector store and cases database)
COPY data/ ./data/

# Create data directory and clear Python cache
RUN mkdir -p /app/data && \
    find /app -name "*.pyc" -delete && \
    find /app -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Set environment variables
ENV PYTHONPATH=/app
ENV VECTOR_STORE_PATH=data/law_vector_store

# Railway will provide PORT environment variable
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Start command for Railway
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "$PORT", "--workers", "1"]
