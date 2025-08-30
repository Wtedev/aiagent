#!/bin/bash
echo "🚀 Starting Legal AI Agent deployment..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r Requirements.txt

# Build FAISS vector store
echo "🔍 Building FAISS vector store..."
cd embeddings && python build_faiss.py && cd ..

echo "✅ Build completed successfully!"
