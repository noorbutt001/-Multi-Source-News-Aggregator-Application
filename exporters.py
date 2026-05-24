from __future__ import annotations

import csv
from pathlib import Path

from news_aggregator.config import EXPORT_DIR
from news_aggregator.models import Article


def export_to_csv(articles: list[Article], output_path: Path | None = None) -> Path:
    output_path = output_path or (EXPORT_DIR / "news_export.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["title", "source", "published_at", "category", "description", "summary", "url"],
        )
        writer.writeheader()
        for article in articles:
            writer.writerow(
                {
                    "title": article.title,
                    "source": article.source,
                    "published_at": article.publication_label,
                    "category": article.category,
                    "description": article.description,
                    "summary": article.summary,
                    "url": article.url,
                }
            )
    return output_path


def export_to_txt(articles: list[Article], output_path: Path | None = None) -> Path:
    output_path = output_path or (EXPORT_DIR / "news_export.txt")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        for index, article in enumerate(articles, start=1):
            file.write(f"[{index}] {article.title}\n")
            file.write(f"Source: {article.source}\n")
            file.write(f"Published: {article.publication_label}\n")
            file.write(f"Category: {article.category}\n")
            file.write(f"Description: {article.description}\n")
            if article.summary:
                file.write(f"Summary: {article.summary}\n")
            file.write(f"URL: {article.url}\n")
            file.write("-" * 80 + "\n")
    return output_path