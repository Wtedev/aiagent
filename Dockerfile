# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY Requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r Requirements.txt

# Copy application code (excluding data files)
COPY backend/ ./backend/
COPY embeddings/ ./embeddings/
COPY pages/ ./pages/
COPY Style/ ./Style/
COPY scrapers/ ./scrapers/
COPY main_app.py ./

# Create data directory for volume mounting
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONPATH=/app
ENV VECTOR_STORE_PATH=/app/data/law_vector_store
ENV PORT=8000

# Expose port
EXPOSE 8000

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🚀 Starting قانونيد Legal AI Agent..."\n\
echo "📁 Checking data directory..."\n\
ls -la /app/data/\n\
echo "🔧 Setting up vector store if needed..."\n\
if [ ! -d "/app/data/law_vector_store" ]; then\n\
    echo "📊 Building FAISS vector store..."\n\
    cd /app/embeddings && python build_faiss.py\n\
    echo "✅ Vector store created!"\n\
else\n\
    echo "✅ Vector store already exists!"\n\
fi\n\
echo "🚀 Starting FastAPI server..."\n\
cd /app && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT\n\
' > /app/start.sh && chmod +x /app/start.sh

# Start the application
CMD ["/app/start.sh"]
