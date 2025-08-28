#!/bin/bash

echo "🚂 Preparing قانونيد Legal AI Agent for Railway Deployment"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "backend/app/main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "✅ Project structure verified"

# Check for required files
echo "📋 Checking required files..."

required_files=(
    "Dockerfile"
    "railway.json"
    "Requirements.txt"
    "backend/app/main.py"
    "data/cases.jsonl"
    "data/laws_index.json"
    "embeddings/build_faiss.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ Missing: $file"
        missing_files=true
    fi
done

if [ "$missing_files" = true ]; then
    echo "❌ Some required files are missing. Please check the project structure."
    exit 1
fi

echo ""
echo "🔧 Checking environment variables..."

# Check if .env exists
if [ -f ".env" ]; then
    echo "✅ .env file found"
    echo "⚠️  Remember to set these in Railway:"
    echo "   - OPENAI_API_KEY"
    echo "   - VECTOR_STORE_PATH=/app/data/law_vector_store"
    echo "   - CORS_ORIGINS=*"
else
    echo "⚠️  No .env file found"
    echo "📝 Create .env file with:"
    echo "   OPENAI_API_KEY=your_key_here"
    echo "   VECTOR_STORE_PATH=data/law_vector_store"
fi

echo ""
echo "📊 Data size summary:"
echo "   - cases.jsonl: $(du -h data/cases.jsonl | cut -f1)"
echo "   - laws_index.json: $(du -h data/laws_index.json | cut -f1)"
echo "   - legal_sources.txt: $(du -h data/legal_sources.txt | cut -f1)"

echo ""
echo "🚀 Ready for Railway deployment!"
echo ""
echo "Next steps:"
echo "1. Push this code to GitHub"
echo "2. Connect your repo to Railway"
echo "3. Create a volume named 'legal-data' mounted at '/app/data'"
echo "4. Set environment variables in Railway"
echo "5. Deploy!"
echo ""
echo "📖 See RAILWAY_DEPLOYMENT.md for detailed instructions"
