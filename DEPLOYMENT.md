# 🚀 Render Deployment Guide

## Prerequisites

1. **GitHub Repository**: Your code must be in a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **OpenAI API Key**: Get your API key from [OpenAI](https://platform.openai.com/api-keys)

## Step-by-Step Deployment

### 1. Prepare Your Repository

Make sure your repository contains:
- ✅ `render.yaml` - Render configuration
- ✅ `runtime.txt` - Python version specification
- ✅ `Requirements.txt` - Python dependencies
- ✅ `build.sh` - Build script (executable)
- ✅ `.gitignore` - Excludes sensitive files

### 2. Connect to Render

1. **Log in to Render Dashboard**
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository**
4. **Select the repository containing your Legal AI Agent**

### 3. Configure the Service

**Service Settings:**
- **Name**: `legal-ai-agent` (or your preferred name)
- **Environment**: `Python`
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave empty (root of repository)

**Build & Deploy Settings:**
- **Build Command**: `pip install -r Requirements.txt && cd embeddings && python build_faiss.py`
- **Start Command**: `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

### 4. Set Environment Variables

**Required Variables:**
- `OPENAI_API_KEY`: Your OpenAI API key (mark as secret)

**Optional Variables:**
- `PYTHON_VERSION`: `3.10.0`
- `CORS_ORIGINS`: `*` (for development)

### 5. Deploy

1. **Click "Create Web Service"**
2. **Wait for the build to complete** (5-10 minutes)
3. **Check the logs** for any errors
4. **Your app will be available at**: `https://your-app-name.onrender.com`

## Expected Build Process

```
🚀 Starting Legal AI Agent deployment...
📦 Installing Python dependencies...
🔍 Building FAISS vector store...
✅ Build completed successfully!
```

## Troubleshooting

### Common Issues

**1. Build Fails - Missing Dependencies**
- Check `Requirements.txt` is complete
- Ensure all imports are available

**2. FAISS Build Error**
- Verify `data/legal_sources_small.txt` exists
- Check `embeddings/build_faiss.py` path

**3. Environment Variables**
- Ensure `OPENAI_API_KEY` is set correctly
- Check variable names match exactly

**4. Port Issues**
- Render uses `$PORT` environment variable
- Don't hardcode port numbers

### Debug Commands

**Check Build Logs:**
- Go to your service dashboard
- Click "Logs" tab
- Look for error messages

**Test Locally First:**
```bash
# Test the exact build process
pip install -r Requirements.txt
cd embeddings && python build_faiss.py
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

## Post-Deployment

### 1. Test Your Application

**Health Check:**
```bash
curl https://your-app-name.onrender.com/health
```

**Virtual Ruling Test:**
```bash
curl -X POST "https://your-app-name.onrender.com/api/virtual" \
  -H "Content-Type: application/json" \
  -d '{"user_query": "قضية بيع سيارة لم تسدد ثمنها"}'
```

### 2. Update Frontend URLs

If your frontend hardcodes localhost URLs, update them to your Render domain.

### 3. Monitor Performance

- **Check Render Dashboard** for resource usage
- **Monitor response times** in the logs
- **Set up alerts** for downtime

## Cost Optimization

**Free Tier Limits:**
- 750 hours/month
- 512MB RAM
- Shared CPU

**Upgrade Considerations:**
- **Starter Plan**: $7/month for dedicated resources
- **Professional Plan**: $25/month for better performance

## Security Notes

1. **Never commit API keys** to your repository
2. **Use environment variables** for all secrets
3. **Enable HTTPS** (automatic on Render)
4. **Set up proper CORS** for production

## Support

- **Render Documentation**: [docs.render.com](https://docs.render.com)
- **Render Community**: [community.render.com](https://community.render.com)
- **GitHub Issues**: For code-specific problems

---

**🎉 Your Legal AI Agent is now live on Render!**
