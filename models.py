from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Article:
    title: str
    source: str
    url: str
    description: str = ""
    published_at: datetime | None = None
    category: str = "general"
    author: str | None = None
    content: str = ""
    summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def publication_label(self) -> str:
        return self.published_at.strftime("%Y-%m-%d %H:%M") if self.published_at else "Unknown"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["published_at"] = self.published_at.isoformat() if self.published_at else None
        return data

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Article":
        published_at = payload.get("published_at")
        if isinstance(published_at, str) and published_at:
            published_at = datetime.fromisoformat(published_at)
        else:
            published_at = None
        return cls(
            title=payload.get("title", ""),
            source=payload.get("source", "Unknown"),
            url=payload.get("url", ""),
            description=payload.get("description", ""),
            published_at=published_at,
            category=payload.get("category", "general"),
            author=payload.get("author"),
            content=payload.get("content", ""),
            summary=payload.get("summary", ""),
            metadata=payload.get("metadata", {}),
        )