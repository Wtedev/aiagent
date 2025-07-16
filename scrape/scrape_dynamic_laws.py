import os
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

#  Config 
INPUT_JSON = "official_law_sources.json"
OUTPUT_DIR = "laws_texts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

#  Selenium Setup 
def init_browser():
    options = Options()
    options.add_argument("--headless")  # Run without opening a window
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

#  Clean HTML 
def clean_html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)

#  Scrape One Page 
def scrape_dynamic_page(url, slug):
    browser = init_browser()
    try:
        print(f"🕵️‍♀️ Visiting {slug}...")
        browser.get(url)
        browser.implicitly_wait(10)  # wait for JS to load
        html = browser.page_source
        clean_text = clean_html_to_text(html)

        if len(clean_text) < 500:
            print(f"⚠️ Still short text for {slug} — may require deeper parsing.")
        else:
            path = os.path.join(OUTPUT_DIR, f"{slug}.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(clean_text)
            print(f"✅ Saved full content to {path}")
    except Exception as e:
        print(f"❌ Error scraping {slug}: {e}")
    finally:
        browser.quit()

#  Main 
def main():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        laws = json.load(f)

    for law in laws:
        slug = law["slug"]
        url = law["url"]

        if slug in ["personal_status_law", "civil_law"]:
            scrape_dynamic_page(url, slug)

if __name__ == "__main__":
    main()