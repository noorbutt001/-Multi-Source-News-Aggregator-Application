from __future__ import annotations

import hashlib
import re
from datetime import datetime
from email.utils import parsedate_to_datetime

from news_aggregator.models import Article


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-zA-Z0-9 ]+", " ", value.lower())).strip()


def article_fingerprint(article: Article) -> str:
    raw = f"{normalize_text(article.title)}|{article.url.strip().lower()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def deduplicate_articles(articles: list[Article]) -> list[Article]:
    seen: set[str] = set()
    unique: list[Article] = []
    for article in articles:
        fingerprint = article_fingerprint(article)
        if fingerprint in seen or not article.url:
            continue
        seen.add(fingerprint)
        unique.append(article)
    return unique


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError, OverflowError):
        return None


def sort_articles(articles: list[Article]) -> list[Article]:
    return sorted(
        articles,
        key=lambda article: article.published_at or datetime.min,
        reverse=True,
    )