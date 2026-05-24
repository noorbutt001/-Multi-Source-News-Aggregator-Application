from __future__ import annotations

import asyncio
import json
from pathlib import Path

from news_aggregator.config import AUTO_REFRESH_SECONDS, CACHE_PATH, DEFAULT_PAGE_SIZE
from news_aggregator.models import Article
from news_aggregator.providers.newsapi import NewsAPIProvider
from news_aggregator.providers.rss import RSSProvider
from news_aggregator.services.summarizer import BasicSummarizer
from news_aggregator.utils.text import deduplicate_articles, sort_articles


class NewsAggregator:
    def __init__(self, cache_path: Path | None = None) -> None:
        self.providers = [NewsAPIProvider(), RSSProvider()]
        self.cache_path = cache_path or CACHE_PATH
        self.summarizer = BasicSummarizer()

    async def latest_news(self, category: str | None = None, page_size: int = DEFAULT_PAGE_SIZE) -> list[Article]:
        return await self._collect(category=category, page_size=page_size)

    async def search_news(self, query: str, category: str | None = None, page_size: int = DEFAULT_PAGE_SIZE) -> list[Article]:
        return await self._collect(category=category, query=query, page_size=page_size)

    async def _collect(
        self,
        *,
        category: str | None = None,
        query: str | None = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> list[Article]:
        results = await asyncio.gather(
            *[
                provider.fetch_latest(category=category, query=query, page_size=page_size)
                for provider in self.providers
            ],
            return_exceptions=True,
        )

        articles: list[Article] = []
        errors: list[str] = []
        for result in results:
            if isinstance(result, Exception):
                errors.append(str(result))
                continue
            articles.extend(result)

        deduped = deduplicate_articles(articles)
        for article in deduped:
            article.summary = self.summarizer.summarize(
                " ".join(part for part in [article.title, article.description, article.content] if part),
                max_sentences=2,
            )
            if errors:
                article.metadata["warnings"] = errors

        ordered = sort_articles(deduped)[:page_size]
        self._cache_results(ordered)
        return ordered

    async def auto_refresh(
        self,
        *,
        category: str | None = None,
        refresh_seconds: int = AUTO_REFRESH_SECONDS,
        iterations: int = 3,
    ) -> list[list[Article]]:
        snapshots: list[list[Article]] = []
        for iteration in range(iterations):
            snapshots.append(await self.latest_news(category=category))
            if iteration < iterations - 1:
                await asyncio.sleep(refresh_seconds)
        return snapshots

    def _cache_results(self, articles: list[Article]) -> None:
        self.cache_path.write_text(
            json.dumps([article.to_dict() for article in articles], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load_cached_results(self) -> list[Article]:
        if not self.cache_path.exists():
            return []
        payload = json.loads(self.cache_path.read_text(encoding="utf-8"))
        return [Article.from_dict(item) for item in payload]