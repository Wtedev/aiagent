# 🧠 Legal AI Agent - القاضي الافتراضي

A sophisticated legal AI system that provides virtual legal rulings based on Saudi Arabian law, built with FastAPI and OpenAI.

## 🌟 Features

- **Virtual Legal Rulings**: Generate detailed legal judgments based on Saudi law
- **Similar Case Analysis**: Find and analyze similar legal cases
- **Arabic Language Support**: Full Arabic interface and responses
- **Islamic Legal Formatting**: Proper Islamic legal document structure
- **Real-time Processing**: Fast response times with optimized FAISS vector search

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd aiagent
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r Requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

5. **Build FAISS vector store**
   ```bash
   cd embeddings && python build_faiss.py && cd ..
   ```

6. **Run the application**
   ```bash
   python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

7. **Access the application**
   - Main page: http://localhost:8000
   - Virtual Ruling: http://localhost:8000/virtual-ruling
   - Chat: http://localhost:8000/chat

## 🏗️ Architecture

```
aiagent/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI application entry point
│       ├── services.py          # Core services (chat, roadmap)
│       ├── chatbot/             # Chat functionality
│       ├── roadmap/             # Roadmap functionality
│       └── virtual/             # Virtual ruling system
├── data/                       # Legal data and vector store
├── embeddings/                 # FAISS vector store builder
├── scrapers/                   # Legal data scraping tools
├── Style/                      # Frontend HTML files
└── Requirements.txt            # Python dependencies
```

## 🔧 API Endpoints

### Virtual Ruling
- **POST** `/api/virtual`
  - Generates virtual legal rulings
  - Request: `{"user_query": "قضية بيع سيارة لم تسدد ثمنها"}`
  - Response: Similar cases, basis of judgment, and final ruling

### Chat
- **POST** `/api/chat`
  - Legal consultation chat
  - Request: `{"question": "سؤال قانوني"}`
  - Response: Detailed legal answer with citations

### Health Check
- **GET** `/health`
  - Application health status

## 🌐 Frontend Pages

- **Homepage** (`/`): Main landing page
- **Virtual Ruling** (`/virtual-ruling`): Virtual legal ruling interface
- **Chat** (`/chat`): Legal consultation chat interface

## 🚀 Deployment

### Render Deployment

1. **Connect your GitHub repository to Render**
2. **Create a new Web Service**
3. **Configure environment variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key
4. **Deploy automatically**

The application will be deployed with the following configuration:
- **Build Command**: `pip install -r Requirements.txt && cd embeddings && python build_faiss.py`
- **Start Command**: `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

## 🔒 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for LLM access | Yes |
| `PYTHON_VERSION` | Python version (default: 3.10) | No |

## 📊 Performance

- **FAISS Vector Search**: Optimized for fast similarity search
- **Reduced Dataset**: 34 key legal sources for faster processing
- **Lazy Loading**: Efficient memory management
- **Caching**: Intelligent response caching

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Saudi Arabian legal system
- OpenAI for LLM capabilities
- FAISS for vector similarity search
- FastAPI for the web framework

---

**Built with ❤️ for the Saudi legal community**
