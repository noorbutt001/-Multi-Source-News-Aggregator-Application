from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console

from news_aggregator.cli import NewsCLI
from news_aggregator.config import CATEGORIES
from news_aggregator.services.aggregator import NewsAggregator
from news_aggregator.services.bookmarks import BookmarkService
from news_aggregator.utils.formatting import build_article_table

app = typer.Typer(help="Professional multi-source news aggregator", invoke_without_command=True)
console = Console()


@app.callback()
def default(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        NewsCLI().run()


@app.command()
def latest(category: str = typer.Option("general", help="general or one of the named categories")) -> None:
    aggregator = NewsAggregator()
    normalized = None if category == "general" else category.lower()
    if normalized and normalized not in CATEGORIES:
        raise typer.BadParameter(f"Category must be one of: {', '.join(CATEGORIES)} or general")
    articles = asyncio.run(aggregator.latest_news(category=normalized))
    console.print(build_article_table(articles))


@app.command()
def search(query: str, category: str = typer.Option("general", help="general or one of the named categories")) -> None:
    aggregator = NewsAggregator()
    normalized = None if category == "general" else category.lower()
    articles = asyncio.run(aggregator.search_news(query=query, category=normalized))
    console.print(build_article_table(articles))


@app.command()
def bookmarks() -> None:
    console.print(build_article_table(BookmarkService().list_bookmarks()))


@app.command()
def gui() -> None:
    command = [sys.executable, "-m", "streamlit", "run", "news_aggregator/gui_streamlit.py"]
    subprocess.run(command, check=False, cwd=Path(__file__).resolve().parent.parent)


if __name__ == "__main__":
    app()