# 🚀 PRODUCTION DOCKERFILE FOR RENDER - MEMORY OPTIMIZED
# This Dockerfile is optimized to work within Render's 512MB free tier limit
# Uses lazy loading and memory optimization techniques

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

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
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command with memory optimization
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--log-level", "info"]
