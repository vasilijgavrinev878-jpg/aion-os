"""
dubiznes.ae — Consolidated scraper
Replaces: scrape_dubiznes.mjs, scrape_dubiznes_final.mjs, scrape_dubiznes_full.mjs, scrape_fixed.mjs

Usage:
  python -m scrapers.dubiznes_scraper collect    # Collect all listing URLs
  python -m scrapers.dubiznes_scraper scrape     # Scrape names & phones
  python -m scrapers.dubiznes_scraper all        # Collect + scrape
  python -m scrapers.dubiznes_scraper fix        # Re-extract from saved listings
"""

import json
import re
import time
import sys
import os
from pathlib import Path
from urllib.request import Request, urlopen
from html import unescape

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

CATEGORIES = [
    "restaurants", "fitness", "education", "healthcare", "real-estate",
    "spa", "clubs-bars", "avtomasterskie-i-deteiling", "organizatsii",
    "gamingclubs", "massage", "uslugi-krasoti-v-oae", "rentacar",
    "russkiye-magazini-v-oae", "meditsina", "it-uslugi", "manikiur-pedikiur",
    "fotograf",
]


# ─── HTTP helpers ──────────────────────────────────────────────

def fetch(url, max_bytes=None):
    """Fetch URL content. If max_bytes set, request only that range."""
    req = Request(url, headers={"User-Agent": USER_AGENT})
    if max_bytes:
        req.add_header("Range", f"bytes=0-{max_bytes - 1}")
    with urlopen(req, timeout=30) as resp:
        data = resp.read()
        if max_bytes:
            return data.decode("utf-8", errors="replace")[:max_bytes]
        return data.decode("utf-8", errors="replace")


# ─── URL extraction ────────────────────────────────────────────

def extract_listing_urls(html):
    """Extract all dubiznes.ae/listing/ URLs from a page."""
    pattern = r'href="(https://dubiznes\.ae/listing/[^/]+/?)"'
    urls = re.findall(pattern, html)
    # Normalize: strip trailing slash
    urls = [u.rstrip("/") for u in urls]
    return list(dict.fromkeys(urls))  # unique, ordered


# ─── Phone extraction ──────────────────────────────────────────

def find_phone_numbers(html):
    """Extract UAE phone numbers (+971...) from HTML."""
    phones = []
    # tel:+971... links
    for m in re.finditer(r'tel:\+?971([0-9\-]{7,12})', html):
        num = "+971" + m.group(1).replace("-", "")
        if num not in phones:
            phones.append(num)
    # Direct +971 numbers
    for m in re.finditer(r'(\+971[0-9]{7,12})', html):
        num = m.group(1)
        if num not in phones:
            phones.append(num)
    return phones


# ─── Name extraction ───────────────────────────────────────────

def extract_name(html):
    """Extract business name from listing page."""
    # Method 1: breadcrumb nav with vnsco-breadcrumbs
    m = re.search(
        r'<nav[^>]*class="[^"]*vnsco-breadcrumbs[^"]*"[^>]*>[\s\S]{0,500}?</nav>',
        html,
    )
    if m:
        spans = re.findall(r'<span[^>]*>([^<]+)</span>', m.group(0))
        texts = [s.strip() for s in spans if s.strip() != "→"]
        if texts:
            return decode_html_entities(texts[-1])

    # Method 2: <title> tag
    m = re.search(r'<title>([^<]+)</title>', html)
    if m:
        title = m.group(1)
        title = re.sub(r"\s*[-–—].*$", "", title)  # strip after dash
        title = re.sub(r"\s+в Дубае.*$", "", title)
        title = re.sub(r"\s+в ОАЭ.*$", "", title)
        title = re.sub(r"\s+в самом сердце.*$", "", title)
        title = title.replace(" - dubiznes.ae", "").replace(" — dubiznes.ae", "")
        return decode_html_entities(title.strip())

    # Method 3: h1 with span
    m = re.search(r'<h1[^>]*>[\s\S]*?<span[^>]*>([^<]+)</span>', html)
    if m:
        return decode_html_entities(m.group(1).strip())

    return None


def decode_html_entities(text):
    """Decode HTML entities and common numeric entities."""
    text = text.replace("&#8212;", "—")
    text = text.replace("&#038;", "&")
    text = text.replace("&#8211;", "–")
    text = text.replace("&#8220;", "\u201c")
    text = text.replace("&#8221;", "\u201d")
    text = text.replace("&#8230;", "\u2026")
    return unescape(text)


# ─── Category page scraping ────────────────────────────────────

def scrape_category(cat):
    """Scrape all listing URLs from a category (handles pagination)."""
    all_urls = []
    page = 1
    while True:
        url = f"https://dubiznes.ae/listing-category/{cat}/"
        if page > 1:
            url = f"https://dubiznes.ae/listing-category/{cat}/page/{page}/"
        print(f"  [{cat}] Page {page}...", end=" ", flush=True)

        try:
            html = fetch(url)
        except Exception as e:
            print(f"ERROR: {e}")
            break

        urls = extract_listing_urls(html)
        for u in urls:
            if u not in all_urls:
                all_urls.append(u)
        print(f"{len(urls)} listings")

        # Check for next page via rel="next"
        next_match = re.search(
            r'<link rel="next"[^>]*href="([^"]+)"', html
        )
        if next_match and f"/page/{page + 1}/" in next_match.group(1):
            page += 1
            time.sleep(0.5)
        else:
            break

    return all_urls


# ─── Listing page scraping ─────────────────────────────────────

def scrape_listing(url, delay=1.5):
    """Scrape a single listing page for name + phone numbers."""
    slug = url.replace("https://dubiznes.ae/listing/", "").rstrip("/")
    try:
        html = fetch(url)
        name = extract_name(html) or slug
        phones = find_phone_numbers(html)
        return {"name": name, "url": url, "phones": phones, "success": True}
    except Exception as e:
        return {"name": slug, "url": url, "phones": [], "success": False, "error": str(e)}


# ─── Fix: re-extract from existing URL list (like scrape_fixed.mjs) ──

def fix_extract(urls_file="dubiznes_listing_urls.json", delay=1.0):
    """Re-extract names/phones from previously saved URL list."""
    filepath = DATA_DIR / urls_file
    if not filepath.exists():
        filepath = Path(urls_file)
        if not filepath.exists():
            print(f"File not found: {urls_file}")
            return

    with open(filepath) as f:
        urls = json.load(f)

    print(f"Re-extracting {len(urls)} listings...")
    results = []
    for i, url in enumerate(urls):
        slug = url.replace("https://dubiznes.ae/listing/", "").rstrip("/")
        print(f"  [{i+1}/{len(urls)}] {slug}...", end=" ", flush=True)

        try:
            # Fetch first 10KB (faster, breadcrumb is in <head>)
            html = fetch(url, max_bytes=10240)
            if not html:
                raise Exception("Empty response")

            name = extract_name(html) or slug
            phones = find_phone_numbers(html)
            results.append({"name": name, "url": url, "phones": phones})
            print(phones[0] if phones else "(no phone)")
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({"name": slug, "url": url, "phones": []})

        time.sleep(delay)

    # Save results
    with_phones = [r for r in results if r["phones"]]
    output_path = DATA_DIR / "dubiznes_final_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(with_phones, f, ensure_ascii=False, indent=2)

    # Also save as JS module
    js_lines = ["const dubiznesData = [\n"]
    for r in with_phones:
        phone_str = "; ".join(f"Телефон: {p}" for p in r["phones"])
        js_lines.append(
            f'  {{ name: {json.dumps(r["name"], ensure_ascii=False)}, '
            f'contact: {json.dumps(phone_str, ensure_ascii=False)}, '
            f'tags: ["phone"] }},\n'
        )
    js_lines.append("];\n")
    js_lines.append(f'console.log("Total businesses:", dubiznesData.length);\n')

    js_path = DATA_DIR / "dubiznes_final_data.js"
    with open(js_path, "w", encoding="utf-8") as f:
        f.writelines(js_lines)

    print(f"\nSaved: {output_path}")
    print(f"Saved: {js_path}")
    print(f"Listings with phones: {len(with_phones)}/{len(results)}")

    # Print summary
    print("\n=== NAME / PHONE PAIRS ===")
    for i, r in enumerate(with_phones):
        print(f"  {i+1}. {r['name']}: {', '.join(r['phones'])}")


# ─── CLI commands ──────────────────────────────────────────────

def cmd_collect():
    """Collect all listing URLs from all categories."""
    all_urls = []
    for cat in CATEGORIES:
        print(f"\nCategory: {cat}")
        urls = scrape_category(cat)
        for u in urls:
            if u not in all_urls:
                all_urls.append(u)
        print(f"  Total so far: {len(all_urls)}")

    print(f"\n=== Total unique listing URLs: {len(all_urls)} ===")
    filepath = DATA_DIR / "dubiznes_listing_urls.json"
    with open(filepath, "w") as f:
        json.dump(all_urls, f, indent=2)
    print(f"Saved to {filepath}")


def cmd_scrape():
    """Scrape all collected listings for names and phone numbers."""
    urls_file = DATA_DIR / "dubiznes_listing_urls.json"
    if not urls_file.exists():
        print(f"Run 'collect' first — {urls_file} not found")
        return

    with open(urls_file) as f:
        all_urls = json.load(f)

    print(f"Scraping {len(all_urls)} listings...")
    results = []
    for i, url in enumerate(all_urls):
        slug = url.replace("https://dubiznes.ae/listing/", "").rstrip("/")
        print(f"  [{i+1}/{len(all_urls)}] {slug}...", end=" ", flush=True)
        result = scrape_listing(url)
        results.append(result)
        if result["phones"]:
            print(", ".join(result["phones"]))
        else:
            print("(no phone)")
        time.sleep(1.5)

    with_phones = [r for r in results if r["phones"]]
    filepath = DATA_DIR / "dubiznes_phone_results.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n=== Results ===")
    print(f"Total: {len(results)}, With phones: {len(with_phones)}")
    for r in with_phones:
        print(f"  {r['name']}: {', '.join(r['phones'])}")


def cmd_all():
    """Collect URLs + scrape listings."""
    cmd_collect()
    cmd_scrape()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]
    commands = {
        "collect": cmd_collect,
        "scrape": cmd_scrape,
        "all": cmd_all,
        "fix": lambda: fix_extract(),
    }

    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
