from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "Multi-Source News Aggregator"
DEFAULT_LANGUAGE = os.getenv("NEWS_LANGUAGE", "en")
DEFAULT_COUNTRY = os.getenv("NEWS_COUNTRY", "us")
DEFAULT_PAGE_SIZE = int(os.getenv("NEWS_PAGE_SIZE", "20"))
HTTP_TIMEOUT_SECONDS = int(os.getenv("NEWS_HTTP_TIMEOUT", "15"))
AUTO_REFRESH_SECONDS = int(os.getenv("NEWS_AUTO_REFRESH_SECONDS", "60"))
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

DATA_DIR = Path(os.getenv("NEWS_DATA_DIR", Path.home() / ".news_aggregator"))
EXPORT_DIR = DATA_DIR / "exports"
BOOKMARKS_PATH = DATA_DIR / "bookmarks.json"
CACHE_PATH = DATA_DIR / "last_results.json"

for path in (DATA_DIR, EXPORT_DIR):
    path.mkdir(parents=True, exist_ok=True)

CATEGORIES = [
    "technology",
    "sports",
    "business",
    "entertainment",
]

RSS_FEEDS: dict[str, list[str]] = {
    "technology": [
        "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "https://www.theverge.com/rss/index.xml",
        "https://www.wired.com/feed/category/gear/latest/rss",
    ],
    "sports": [
        "https://www.espn.com/espn/rss/news",
        "https://feeds.bbci.co.uk/sport/rss.xml",
        "https://sports.yahoo.com/rss/",
    ],
    "business": [
        "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
        "https://www.cnbc.com/id/10001147/device/rss/rss.html",
        "https://feeds.bbci.co.uk/news/business/rss.xml",
    ],
    "entertainment": [
        "https://www.hollywoodreporter.com/feed/",
        "https://variety.com/feed/",
        "https://www.billboard.com/feed/",
    ],
    "general": [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "https://feeds.skynews.com/feeds/rss/home.xml",
    ],
}