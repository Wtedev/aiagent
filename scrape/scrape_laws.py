import os
import json
import requests
from bs4 import BeautifulSoup

#  Configuration 
INPUT_JSON = "official_law_sources.json"
OUTPUT_DIR = "laws_texts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

#  Clean HTML Content 
def clean_html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Remove irrelevant tags
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # Extract readable text
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)

#  Scrape and Save 
def scrape_and_save(url: str, slug: str):
    try:
        print(f"📥 Scraping {slug} from {url}")
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        clean_text = clean_html_to_text(response.text)

        # Save to file
        path = os.path.join(OUTPUT_DIR, f"{slug}.txt")
        with open(path, "w", encoding="utf-8") as file:
            file.write(clean_text)

        print(f"✅ Saved clean content to {path}")
    except Exception as e:
        print(f"❌ Error scraping {slug}: {e}")

# ========== Main ==========
def main():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        laws = json.load(f)

    for law in laws:
        scrape_and_save(url=law["url"], slug=law["slug"])

if __name__ == "__main__":
    main()