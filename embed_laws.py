import os
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    print("❌ OPENAI_API_KEY not found.")
    exit(1)

LAWS_FOLDER = "laws_texts"
VECTOR_STORE_DIR = "law_vector_store"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=openai_key)
splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

# Prepare Documents
all_docs = []

for filename in os.listdir(LAWS_FOLDER):
    if filename.endswith(".txt"):
        domain = filename.replace(".txt", "")
        filepath = os.path.join(LAWS_FOLDER, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        chunks = splitter.create_documents([content], metadatas=[{"source": domain}])
        all_docs.extend(chunks)
        print(f"✅ Chunked {filename} into {len(chunks)} pieces.")

#  Embed & Save 
print("🔍 Embedding and saving to FAISS...")
vector_db = FAISS.from_documents(all_docs, embedding_model)
vector_db.save_local(VECTOR_STORE_DIR)
print(f"✅ Saved vector store to '{VECTOR_STORE_DIR}' with {len(all_docs)} chunks.")