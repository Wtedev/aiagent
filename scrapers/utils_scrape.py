
import re
import time
import requests
from bs4 import BeautifulSoup
def extract_urls(text: str) -> list[str]:
    """Extracts all valid URLs from a block of text."""
    return re.findall(r'https?://[^\s)>\]"\'<>]+', text)

def clean_text(text: str) -> str:
    """Clean raw HTML or scraped text by removing excess whitespace and formatting issues."""
    text = re.sub(r'\s+', ' ', text)  # Normalize all whitespace
    text = re.sub(r'\n{3,}', '\n\n', text.strip())  # Limit line breaks
    return text.strip()

def fetch_html(url: str, headers=None, timeout=10) -> str:
    """Fetch raw HTML content from a URL with retry and timeout support."""
    try:
        response = requests.get(url, headers=headers or {}, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"❌ Error fetching {url}: {e}")
        return ""

def extract_visible_text(html: str) -> str:
    """Extract visible text from HTML using BeautifulSoup."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted elements
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    return clean_text(text)

def robust_scrape(url: str, retries: int = 3, delay: float = 2.0) -> str:
    """Attempt to scrape and clean visible text from a webpage with retries."""
    for attempt in range(1, retries + 1):
        print(f"🔎 Attempt {attempt} to scrape: {url}")
        html = fetch_html(url)
        if html:
            return extract_visible_text(html)
        time.sleep(delay)
    print(f"❌ Failed to scrape after {retries} attempts: {url}")
    return ""