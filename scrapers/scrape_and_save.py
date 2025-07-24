from __future__ import annotations
import json, pathlib, re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from utils_scrape import SESSION, clean_text  

def fetch_articles(law_id):
    url = f"https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/{law_id}/1"
    response = SESSION.get(url)
    if not response.ok:
        print(f"❌ Failed to fetch law: {law_id}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []
    current_part = None

    for article in soup.find_all("div", class_="article_item"):
        title_elem = article.find("h3", class_="center")
        content_elem = article.find("div", class_="HTMLContainer")
        if not title_elem or not content_elem:
            continue

        title = title_elem.get_text(strip=True)
        content = content_elem.get_text(separator="\n", strip=True)

        if re.match(r"^(الباب|الفصل)\s", title):
            current_part = title
            continue

        amendments = []
        amend_link = article.find("a", class_="ancArticlePrevVersions")
        if amend_link and amend_link.has_attr("data-articleid"):
            amend_id = amend_link["data-articleid"]
            amend_div = soup.find("div", class_=f"{amend_id} popup-list")
            if amend_div:
                html_blocks = amend_div.find_all("div", class_="HTMLContainer")
                for block in html_blocks:
                    text = block.get_text(strip=True)
                    if text:
                        amendments.append({"text": text})

        articles.append({
            "title": title,
            "content": content,
            "part": current_part,
            "amendments": amendments if amendments else None
        })

    return articles

def extract_metadata(soup):
    meta = {}
    try:
        info_box = soup.select_one("div.system_info")
        for row in info_box.select("div"):
            label_elem = row.select_one("label")
            value_elem = row.select_one("span")
            if label_elem and value_elem:
                label = label_elem.text.strip()
                value = value_elem.text.strip()
                meta[label] = value
    except Exception:
        pass

    try:
        desc_elem = soup.select_one("div.system_brief .HTMLContainer")
        meta["نبذة عن النظام"] = desc_elem.get_text(" ", strip=True) if desc_elem else ""
    except Exception:
        meta["نبذة عن النظام"] = ""

    return meta

def read_sources(path="data/legal_sources.txt") -> list[dict]:
    sources = []
    with open(path, encoding="utf8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            url, name = line.split("#")
            law_id = url.split("/")[-2]
            sources.append({
                "law_id": law_id,
                "name": name.strip(),
                "url": url.strip()
            })
    return sources

def main():
    sources = read_sources()
    final_data = []

    for law in sources:
        print(f"📘 Fetching: {law['name']}")
        url = f"https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/{law['law_id']}/1"
        r = SESSION.get(url)
        if not r.ok:
            print(f"❌ Failed: {law['law_id']}")
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        law["metadata"] = extract_metadata(soup)
        law["articles"] = fetch_articles(law["law_id"])
        final_data.append(law)

    out_path = pathlib.Path("data/laws_index.json")
    out_path.write_text(json.dumps({
        "generated_at": datetime.now().isoformat(),
        "laws": final_data
    }, ensure_ascii=False, indent=2), encoding="utf8")

    print("✅ Saved:", out_path)

if __name__ == "__main__":
    main()