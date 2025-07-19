import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from embeddings.text_splitter import create_splitter  # make sure this module exists

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise EnvironmentError("❌ OPENAI_API_KEY is missing in .env")

# Configurations
VECTOR_DIR = "data/law_vector_store"
TEXTS_DIR = "data/laws_texts"
CHUNK_BATCH_SIZE = 200

# Initialize tools
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=api_key
)
splitter = create_splitter()

# Read all text files
all_docs = []
for filename in os.listdir(TEXTS_DIR):
    if filename.endswith(".txt"):
        file_path = os.path.join(TEXTS_DIR, filename)
        with open(file_path, encoding='utf-8') as f:
            raw = f.read().strip()
            if raw:
                chunks = splitter.create_documents([raw], metadatas=[{"source": filename}])
                all_docs.extend(chunks)

if not all_docs:
    raise ValueError("❌ No valid text documents found to embed.")

print(f"🧠 Embedding {len(all_docs)} documents in batches...")

# Helper to split list into batches
def batchify(lst, batch_size):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]

# Embed in batches
stores = []
for batch in batchify(all_docs, CHUNK_BATCH_SIZE):
    print(f"🔢 Embedding batch of {len(batch)} chunks...")
    store = FAISS.from_documents(batch, embedding_model)
    stores.append(store)

# Merge all stores
vector_db = stores[0]
for other in stores[1:]:
    vector_db.merge_from(other)

# Save final store
vector_db.save_local(VECTOR_DIR)
print(f"✅ Saved FAISS vector store at '{VECTOR_DIR}'")