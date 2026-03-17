"""
Utility: Fetch and parse OpenROAD documentation pages for knowledge base enrichment.
Run this script to download additional documentation from the web.
Usage: python -m backend.doc_fetcher
"""

import re
import json
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
    FETCH_AVAILABLE = True
except ImportError:
    FETCH_AVAILABLE = False
    print("requests/beautifulsoup4 not installed. Skipping doc fetching.")


DOC_URLS = [
    "https://openroad.readthedocs.io/en/latest/main/README.html",
    "https://openroad.readthedocs.io/en/latest/",
]


def fetch_page(url: str, timeout: int = 15) -> str:
    """Fetch and extract text content from a URL."""
    if not FETCH_AVAILABLE:
        return ""
    try:
        headers = {"User-Agent": "OpenROAD-AI-Assistant/1.0"}
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code != 200:
            print(f"Failed {url}: {resp.status_code}")
            return ""
        soup = BeautifulSoup(resp.text, "lxml")
        # Remove nav, header, footer elements
        for tag in soup.select("nav,header,footer,.sidebar,.toc"):
            tag.decompose()
        
        # Get main content
        main = soup.find("main") or soup.find("div", class_="document") or soup.body
        if not main:
            return ""
        
        text = main.get_text(separator="\n", strip=True)
        # Clean up whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text[:10000]  # Limit size
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks


def save_fetched_docs(docs: list, output_path: str = "./data/fetched_docs.json"):
    """Save fetched docs to JSON."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(docs, f, indent=2)
    print(f"Saved {len(docs)} chunks to {output_path}")


if __name__ == "__main__":
    all_docs = []
    for i, url in enumerate(DOC_URLS):
        print(f"Fetching: {url}")
        text = fetch_page(url)
        if text:
            chunks = chunk_text(text)
            for j, chunk in enumerate(chunks):
                all_docs.append({
                    "id": f"web_{i:02d}_{j:03d}",
                    "title": f"OpenROAD Docs (web) - Chunk {j+1}",
                    "category": "web_docs",
                    "content": chunk,
                    "source": url,
                    "tags": ["openroad", "documentation", "web"]
                })
            print(f"  → {len(chunks)} chunks extracted")
        else:
            print(f"  → No content extracted")

    if all_docs:
        save_fetched_docs(all_docs)
    else:
        print("No docs fetched.")
