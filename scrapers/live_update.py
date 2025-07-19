
import os
import re
from dotenv import load_dotenv
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from crewai_tools import ScrapeWebsiteTool
from scrapers.utils_scrape import clean_text, extract_urls

# Load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise EnvironmentError("❌ Missing OPENAI_API_KEY in .env")

# Configuration
VECTOR_DB_PATH = "data/law_vector_store"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Initialize embedding and splitter
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=api_key)
splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

# Load existing FAISS store or create new
if os.path.exists(VECTOR_DB_PATH):
    vector_db = FAISS.load_local(VECTOR_DB_PATH, embeddings=embedding_model, allow_dangerous_deserialization=True)
else:
    vector_db = None

# Load URLs from source file
SOURCE_FILE = "data/legal_sources.txt"
with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
    urls = extract_urls(f.read())

for i, url in enumerate(urls, 1):
    print(f"🔍 Scraping {i}: {url}")
    try:
        scraper = ScrapeWebsiteTool(website_url=url)
        raw_text = scraper.run()
        cleaned = clean_text(raw_text)

        chunks = splitter.create_documents([cleaned], metadatas=[{"source": url}])

        if vector_db:
            vector_db.add_documents(chunks)
        else:
            vector_db = FAISS.from_documents(chunks, embedding_model)

        print(f"✅ Embedded {len(chunks)} chunks from {url}")

    except Exception as e:
        print(f"❌ Failed to process {url}: {e}")

# Save updated store
if vector_db:
    vector_db.save_local(VECTOR_DB_PATH)
    print(f"💾 Updated FAISS store saved to {VECTOR_DB_PATH}")
else:
    print("⚠️ No valid documents found to embed.")