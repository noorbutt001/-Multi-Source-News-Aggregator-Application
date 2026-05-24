from __future__ import annotations

import asyncio
from typing import Any

import feedparser

from news_aggregator.config import RSS_FEEDS
from news_aggregator.models import Article
from news_aggregator.providers.base import NewsProvider
from news_aggregator.utils.text import parse_datetime


class RSSProvider(NewsProvider):
    name = "RSS"

    async def fetch_latest(
        self,
        *,
        category: str | None = None,
        query: str | None = None,
        page_size: int = 20,
    ) -> list[Article]:
        selected_category = category or "general"
        feeds = RSS_FEEDS.get(selected_category, RSS_FEEDS["general"])
        tasks = [asyncio.to_thread(feedparser.parse, feed_url) for feed_url in feeds]
        parsed_feeds = await asyncio.gather(*tasks, return_exceptions=True)

        articles: list[Article] = []
        for parsed in parsed_feeds:
            if isinstance(parsed, Exception):
                continue
            articles.extend(self._extract_articles(parsed, selected_category, query))
        return articles[:page_size]

    def _extract_articles(self, parsed_feed: Any, category: str, query: str | None) -> list[Article]:
        feed_title = parsed_feed.feed.get("title", self.name)
        articles: list[Article] = []
        for entry in parsed_feed.entries:
            title = entry.get("title", "Untitled")
            description = entry.get("summary", "")
            content = " ".join(part.get("value", "") for part in entry.get("content", []))
            haystack = f"{title} {description} {content}".lower()
            if query and query.lower() not in haystack:
                continue
            articles.append(
                Article(
                    title=title,
                    source=entry.get("source", {}).get("title") or feed_title,
                    url=entry.get("link", ""),
                    description=description,
                    published_at=parse_datetime(entry.get("published") or entry.get("updated")),
                    category=category,
                    author=entry.get("author"),
                    content=content,
                    metadata={"provider": self.name},
                )
            )
        return articles