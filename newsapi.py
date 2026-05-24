from __future__ import annotations

from datetime import datetime
from typing import Any

import aiohttp

from news_aggregator.config import DEFAULT_COUNTRY, DEFAULT_LANGUAGE, HTTP_TIMEOUT_SECONDS, NEWSAPI_KEY
from news_aggregator.models import Article
from news_aggregator.providers.base import NewsProvider


class NewsAPIProvider(NewsProvider):
    name = "NewsAPI"
    base_url = "https://newsapi.org/v2"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or NEWSAPI_KEY

    async def fetch_latest(
        self,
        *,
        category: str | None = None,
        query: str | None = None,
        page_size: int = 20,
    ) -> list[Article]:
        if not self.api_key:
            return []

        endpoint = "/everything" if query else "/top-headlines"
        params: dict[str, Any] = {
            "apiKey": self.api_key,
            "pageSize": max(1, min(page_size, 100)),
            "language": DEFAULT_LANGUAGE,
        }
        if query:
            params["q"] = query
            params["sortBy"] = "publishedAt"
        else:
            params["country"] = DEFAULT_COUNTRY
            if category and category != "general":
                params["category"] = category

        timeout = aiohttp.ClientTimeout(total=HTTP_TIMEOUT_SECONDS)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                if response.status != 200:
                    detail = await response.text()
                    raise RuntimeError(f"NewsAPI error {response.status}: {detail[:200]}")
                payload = await response.json()

        if payload.get("status") != "ok":
            raise RuntimeError(payload.get("message", "Unknown NewsAPI error"))

        return [self._to_article(item, category or "general") for item in payload.get("articles", [])]

    def _to_article(self, item: dict[str, Any], category: str) -> Article:
        published_at = None
        raw_published = item.get("publishedAt")
        if raw_published:
            try:
                published_at = datetime.fromisoformat(raw_published.replace("Z", "+00:00"))
            except ValueError:
                published_at = None

        return Article(
            title=item.get("title") or "Untitled",
            source=(item.get("source") or {}).get("name", self.name),
            url=item.get("url") or "",
            description=item.get("description") or "",
            published_at=published_at,
            category=category,
            author=item.get("author"),
            content=item.get("content") or "",
            metadata={"provider": self.name},
        )