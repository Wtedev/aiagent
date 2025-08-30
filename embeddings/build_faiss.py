import os
import json
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# Load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("❌ Missing OPENAI_API_KEY in .env")

# Config
LAWS_INDEX_PATH = "../data/laws_index.json"
VECTOR_DB_PATH = "../data/law_vector_store"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_CHUNK_LENGTH = 4000  # ~1500 tokens

# Initialize tools
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=api_key
)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
)

# Load laws data
with open(LAWS_INDEX_PATH, encoding="utf8") as f:
    db = json.load(f)

docs = []
for law in db["laws"]:
    for article in law.get("articles", []):
        content = article.get("content", "")
        if not content:
            continue

        # ⬛ Main article chunks
        metadata = {
            "law_id": law["law_id"],
            "law_name": law["name"],
            "article_title": article.get("title", ""),
            "part": article.get("part"),
            "url": law["url"]
        }

        chunks = splitter.create_documents([content], metadatas=[metadata])
        for chunk in chunks:
            if len(chunk.page_content) < MAX_CHUNK_LENGTH:
                docs.append(chunk)

        # 🟦 Amendments (if any)
        for amendment in article.get("amendments", []) or []:
            amend_text = amendment.get("text", "")
            amend_url = amendment.get("source_url", law["url"])  # fallback to law url

            amend_metadata = {
                "law_id": law["law_id"],
                "law_name": law["name"],
                "article_title": article.get("title", ""),
                "part": article.get("part"),
                "url": amend_url,
                "is_amendment": True  # Helpful flag
            }

            amend_chunks = splitter.create_documents([amend_text], metadatas=[amend_metadata])
            for chunk in amend_chunks:
                if len(chunk.page_content) < MAX_CHUNK_LENGTH:
                    docs.append(chunk)

if not docs:
    raise ValueError("❌ No valid chunks found to embed.")

print(f"🧠 Prepared {len(docs)} chunks . Generating embeddings...")


# Split docs into safe batches
def batch_chunks(lst, batch_size):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]

print("🧠 Generating embeddings in safe batches...")
all_vectors = None

for i, doc_batch in enumerate(batch_chunks(docs, 500)):
    print(f"→ Embedding batch {i + 1} ({len(doc_batch)} docs)...")
    partial_vector = FAISS.from_documents(doc_batch, embedding_model)
    if all_vectors is None:
        all_vectors = partial_vector
    else:
        all_vectors.merge_from(partial_vector)

# Save final vector store
all_vectors.save_local(VECTOR_DB_PATH)
print(f"✅ FAISS vector store saved to {VECTOR_DB_PATH}")
print(f"✅ FAISS vector store saved to {VECTOR_DB_PATH}")