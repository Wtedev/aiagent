import os
import re
import json
from dotenv import load_dotenv
from crewai_tools import ScrapeWebsiteTool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# Load API key
load_dotenv()

SOURCE_FILE = "data/legal_sources.txt"
OUTPUT_DIR = "data/laws_texts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

url_pattern = r'https?://[\S]+'


def scrape_static_sources():
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        urls = re.findall(url_pattern, f.read())

    all_documents = []
    for i, url in enumerate(urls, start=1):
        try:
            print(f"🔍 Scraping {i}: {url}")
            text = ScrapeWebsiteTool(website_url=url).run()
            clean_text = re.sub(r'\n{3,}', '\n\n', text.strip())

            file_path = os.path.join(OUTPUT_DIR, f"law_{i}.txt")
            with open(file_path, 'w', encoding='utf-8') as out:
                out.write(clean_text)

            chunks = splitter.create_documents([clean_text], metadatas=[{"source": url}])
            all_documents.extend(chunks)
            print(f"✅ Saved and chunked law_{i}.txt into {len(chunks)} chunks.")

        except Exception as e:
            print(f"❌ Failed to scrape {url}: {e}")
    return all_documents

if __name__ == '__main__':
    scrape_static_sources()
