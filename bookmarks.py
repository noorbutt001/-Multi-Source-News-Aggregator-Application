from __future__ import annotations

import json
from pathlib import Path

from news_aggregator.config import BOOKMARKS_PATH
from news_aggregator.models import Article


class BookmarkService:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or BOOKMARKS_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def list_bookmarks(self) -> list[Article]:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return [Article.from_dict(item) for item in payload]

    def add(self, article: Article) -> None:
        bookmarks = self.list_bookmarks()
        if any(existing.url == article.url for existing in bookmarks):
            return
        bookmarks.append(article)
        self._save(bookmarks)

    def remove(self, url: str) -> bool:
        bookmarks = self.list_bookmarks()
        filtered = [article for article in bookmarks if article.url != url]
        changed = len(filtered) != len(bookmarks)
        if changed:
            self._save(filtered)
        return changed

    def _save(self, articles: list[Article]) -> None:
        self.path.write_text(
            json.dumps([article.to_dict() for article in articles], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )