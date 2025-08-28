#!/bin/bash

echo "🚀 Starting قانونيد Legal AI Agent on Railway..."
echo "📁 Current directory: $(pwd)"
echo "📁 Data directory contents:"
ls -la /app/data/

# Check if we're on Railway
if [ -n "$PORT" ]; then
    echo "🚂 Running on Railway with PORT: $PORT"
else
    echo "⚠️  Not running on Railway"
fi

# Check if vector store exists
if [ ! -d "/app/data/law_vector_store" ]; then
    echo "📊 Building FAISS vector store..."
    echo "🔑 Checking OpenAI API key..."
    
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "❌ ERROR: OPENAI_API_KEY environment variable is not set!"
        echo "Please set it in Railway environment variables."
        exit 1
    fi
    
    echo "✅ OpenAI API key found, building vector store..."
    cd /app/embeddings
    python build_faiss.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Vector store created successfully!"
    else
        echo "❌ Failed to create vector store!"
        exit 1
    fi
    
    cd /app
else
    echo "✅ Vector store already exists!"
fi

# Check final data structure
echo "📁 Final data directory structure:"
ls -la /app/data/
echo "📊 Vector store size:"
du -sh /app/data/law_vector_store/ 2>/dev/null || echo "Vector store not found"

# Start the FastAPI server
echo "🚀 Starting FastAPI server on port $PORT..."
cd /app
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
