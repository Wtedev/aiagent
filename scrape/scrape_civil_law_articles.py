import os
import requests
from bs4 import BeautifulSoup
import json

#  Config 
URL = "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/f0eaae46-9f84-40ee-815e-a9a700f268b3/1"
OUTPUT_TXT = "laws_texts/civil_law.txt"
OUTPUT_JSON = "laws_texts/civil_law_articles.json"
os.makedirs("laws_texts", exist_ok=True)

#  Extract and Annotate 
def extract_articles(html):
    soup = BeautifulSoup(html, "html.parser")
    all_text = soup.get_text(separator="\n")

    lines = all_text.splitlines()
    articles = []
    current_article = {"title": None, "text": "", "amended": False, "repealed": False}

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("المادة"):
            # Save previous article
            if current_article["title"]:
                articles.append(current_article)

            # Start new article
            current_article = {
                "title": stripped,
                "text": "",
                "amended": "معدلة" in stripped,
                "repealed": "ملغاة" in stripped
            }
        elif stripped:
            current_article["text"] += stripped + "\n"

    # Save last article
    if current_article["title"]:
        articles.append(current_article)

    return articles

#  Main 
def main():
    print("📥 Fetching civil law with amendment tracking...")
    res = requests.get(URL, timeout=20)
    res.raise_for_status()

    articles = extract_articles(res.text)

    # Save to .json
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f_json:
        json.dump(articles, f_json, ensure_ascii=False, indent=2)
        print(f"✅ Saved articles with metadata to {OUTPUT_JSON}")

    full_text = "\n\n".join([f"{a['title']}\n{a['text'].strip()}" for a in articles])
    with open(OUTPUT_TXT, "w", encoding="utf-8") as f_txt:
        f_txt.write(full_text)
        print(f"✅ Saved full law text to {OUTPUT_TXT}")

if __name__ == "__main__":
    main()