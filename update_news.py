import json, re
from datetime import datetime
from zoneinfo import ZoneInfo
import feedparser

# Open RSS feeds (no API key)
FEEDS = [
    ("Yahoo Finance - Top Stories", "https://feeds.finance.yahoo.com/rss/2.0/headline?s=yhoo&region=US&lang=en-US"),
    ("CNBC - Top News", "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
    ("MarketWatch - Top Stories", "https://feeds.marketwatch.com/marketwatch/topstories/"),
    ("AP Business", "https://apnews.com/hub/business?rss=1"),
]

def clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()

def format_date(entry) -> str:
    # RSS dates vary; keep it simple
    for key in ("published_parsed", "updated_parsed"):
        if hasattr(entry, key) and getattr(entry, key):
            dt = datetime(*getattr(entry, key)[:6], tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/Los_Angeles"))
            return dt.strftime("%b %d, %Y")
    return "—"

def main():
    pool = []
    used_sources = []

    BLOCK_WORDS = ["election", "politics", "trump", "biden", "campaign"]
    for source, url in FEEDS:
        used_sources.append(source)
        feed = feedparser.parse(url)
        for e in feed.entries[:15]:
            title = clean(getattr(e, "title", ""))
            link = clean(getattr(e, "link", ""))
            if title and link:
                pool.append({
                    "title": title,
                    "link": link,
                    "source": source,
                    "published": format_date(e)
                })

    # Pick first 3 unique titles
    seen = set()
    top = []
    for it in pool:
        key = it["title"].lower()
        if key not in seen:
            seen.add(key)
            top.append(it)
        if len(top) == 3:
            break

    updated = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%b %d, %Y %I:%M %p PT")

    out = {
        "updated_local": updated,
        "sources": used_sources,
        "items": top if top else [{
            "title": "No headlines found (feeds may be temporarily down).",
            "link": "https://github.com",
            "source": "System",
            "published": "—"
        }]
    }

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
