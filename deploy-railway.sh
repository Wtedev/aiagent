#!/bin/bash

echo "🚀 Deploying Legal AI Agent to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Create new project (if not exists)
echo "🏗️ Creating Railway project..."
railway init

# Set environment variables
echo "🔧 Setting environment variables..."
railway variables set OPENAI_API_KEY="$OPENAI_API_KEY"
railway variables set VECTOR_STORE_PATH="data/law_vector_store"
railway variables set CORS_ORIGINS="*"

# Deploy
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "🌐 Your app will be available at the Railway URL"
echo "📊 Check status with: railway status"
