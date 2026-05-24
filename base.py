from __future__ import annotations

from abc import ABC, abstractmethod

from news_aggregator.models import Article


class NewsProvider(ABC):
    name: str

    @abstractmethod
    async def fetch_latest(
        self,
        *,
        category: str | None = None,
        query: str | None = None,
        page_size: int = 20,
    ) -> list[Article]:
        raise NotImplementedError