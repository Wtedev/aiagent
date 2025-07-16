import os
import re
from dotenv import load_dotenv
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from crewai_tools import ScrapeWebsiteTool

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    print("❌ OPENAI_API_KEY not found in .env file")
    exit(1)

SOURCE_FILE = "legal_sources.txt"
TEXT_OUTPUT_DIR = "laws_texts"
VECTOR_OUTPUT_DIR = "law_vector_store_lolo"
os.makedirs(TEXT_OUTPUT_DIR, exist_ok=True)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=openai_api_key)

url_pattern = r'https?://[^\s)>\]"\'<>]+'
with open(SOURCE_FILE, 'r', encoding='utf-8') as file:
    content = file.read()
    urls = re.findall(url_pattern, content)

documents = []
for i, url in enumerate(urls, start=1):
    try:
        print(f"🔍 Scraping {i}: {url}")
        scraper = ScrapeWebsiteTool(website_url=url)
        page_text = scraper.run()

        clean_text = re.sub(r'\n{3,}', '\n\n', page_text.strip())

        filename = f"law_{i}.txt"
        file_path = os.path.join(TEXT_OUTPUT_DIR, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(clean_text)

        chunks = splitter.create_documents([clean_text], metadatas=[{"source": url}])
        documents.extend(chunks)

        print(f"✅ Saved and chunked {filename} into {len(chunks)} chunks.")

    except Exception as e:
        print(f"❌ Failed to scrape {url}: {e}")
        continue

documents = [doc for doc in documents if doc.page_content.strip()]
if not documents:
    print("❌ No valid documents to embed. Exiting.")
    exit(1)



if not documents:
    print("❌ No documents to embed. Exiting.")
    exit(1)

print("🧠 Embedding documents and saving FAISS vector store...")

def batchify(lst, batch_size):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]

batch_size = 200
all_stores = []

for batch in batchify(documents, batch_size):
    store = FAISS.from_documents(batch, embedding_model)
    all_stores.append(store)

final_store = all_stores[0]
for store in all_stores[1:]:
    final_store.merge_from(store)

final_store.save_local(VECTOR_OUTPUT_DIR)
print(f"✅ FAISS store saved successfully at '{VECTOR_OUTPUT_DIR}' with {len(documents)} chunks (batched).")
