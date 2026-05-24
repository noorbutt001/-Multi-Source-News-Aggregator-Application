from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt

from news_aggregator.config import AUTO_REFRESH_SECONDS, CATEGORIES, EXPORT_DIR
from news_aggregator.models import Article
from news_aggregator.services.aggregator import NewsAggregator
from news_aggregator.services.bookmarks import BookmarkService
from news_aggregator.services.exporters import export_to_csv, export_to_txt
from news_aggregator.utils.formatting import build_article_panel, build_article_table


class NewsCLI:
    def __init__(self) -> None:
        self.console = Console()
        self.aggregator = NewsAggregator()
        self.bookmarks = BookmarkService()
        self.last_results: list[Article] = self.aggregator.load_cached_results()

    def run(self) -> None:
        self.console.print(Panel.fit("[bold cyan]Multi-Source News Aggregator[/bold cyan]"))
        while True:
            self.console.print(
                "\n[bold]Menu[/bold]\n"
                "1. View Latest News\n"
                "2. Search News\n"
                "3. Select Category\n"
                "4. View Bookmarks\n"
                "5. Save Articles to File\n"
                "6. Auto-Refresh Latest News\n"
                "7. Launch GUI\n"
                "8. Exit"
            )
            choice = Prompt.ask("Choose an option", default="1").strip()
            try:
                if choice == "1":
                    self.view_latest_news()
                elif choice == "2":
                    self.search_news()
                elif choice == "3":
                    self.select_category()
                elif choice == "4":
                    self.view_bookmarks()
                elif choice == "5":
                    self.save_articles()
                elif choice == "6":
                    self.auto_refresh_news()
                elif choice == "7":
                    self.launch_gui()
                elif choice == "8":
                    self.console.print("[bold green]Goodbye![/bold green]")
                    break
                else:
                    self.console.print("[bold red]Invalid option. Try again.[/bold red]")
            except KeyboardInterrupt:
                self.console.print("\n[bold yellow]Operation cancelled.[/bold yellow]")
            except Exception as exc:  # pragma: no cover - defensive CLI branch
                self.console.print(f"[bold red]Error:[/bold red] {exc}")

    def view_latest_news(self, category: str | None = None) -> None:
        label = category.title() if category else "Latest"
        self.console.print(f"[cyan]Fetching {label} news...[/cyan]")
        articles = asyncio.run(self.aggregator.latest_news(category=category))
        self._display_results(articles, title=f"{label} News")

    def search_news(self, query: str | None = None, category: str | None = None) -> None:
        query = query or Prompt.ask("Keyword")
        self.console.print(f"[cyan]Searching for '{query}'...[/cyan]")
        articles = asyncio.run(self.aggregator.search_news(query=query, category=category))
        self._display_results(articles, title=f"Search Results: {query}")

    def select_category(self) -> None:
        self.console.print("\n[bold]Categories[/bold]")
        for index, category in enumerate(CATEGORIES, start=1):
            self.console.print(f"{index}. {category.title()}")
        selected = IntPrompt.ask("Category number", default=1)
        if 1 <= selected <= len(CATEGORIES):
            self.view_latest_news(CATEGORIES[selected - 1])
        else:
            self.console.print("[bold red]Invalid category selection.[/bold red]")

    def view_bookmarks(self) -> None:
        bookmarks = self.bookmarks.list_bookmarks()
        if not bookmarks:
            self.console.print("[yellow]No bookmarks saved yet.[/yellow]")
            return
        self.console.print(build_article_table(bookmarks))
        action = Prompt.ask("Bookmark action", choices=["view", "remove", "back"], default="back")
        if action == "back":
            return
        index = IntPrompt.ask("Article number", default=1)
        if not (1 <= index <= len(bookmarks)):
            self.console.print("[bold red]Invalid article selection.[/bold red]")
            return
        article = bookmarks[index - 1]
        if action == "view":
            self.console.print(build_article_panel(article))
        elif action == "remove":
            removed = self.bookmarks.remove(article.url)
            self.console.print("[green]Bookmark removed.[/green]" if removed else "[yellow]Bookmark not found.[/yellow]")

    def save_articles(self) -> None:
        if not self.last_results:
            self.console.print("[yellow]No loaded articles. Fetch or search news first.[/yellow]")
            return
        export_format = Prompt.ask("Format", choices=["csv", "txt"], default="csv")
        default_path = EXPORT_DIR / f"saved_articles.{export_format}"
        target = Prompt.ask("Output file path", default=str(default_path))
        path = Path(target)
        saved_path = export_to_csv(self.last_results, path) if export_format == "csv" else export_to_txt(self.last_results, path)
        self.console.print(f"[green]Articles saved to {saved_path}[/green]")

    def auto_refresh_news(self) -> None:
        category_choice = Prompt.ask("Category", choices=["general", *CATEGORIES], default="general")
        refresh_seconds = IntPrompt.ask("Refresh seconds", default=AUTO_REFRESH_SECONDS)
        iterations = IntPrompt.ask("Number of refresh cycles", default=3)
        snapshots = asyncio.run(
            self.aggregator.auto_refresh(
                category=None if category_choice == "general" else category_choice,
                refresh_seconds=refresh_seconds,
                iterations=iterations,
            )
        )
        for index, articles in enumerate(snapshots, start=1):
            self.console.print(Panel.fit(f"Refresh Cycle {index}"))
            self._display_results(articles, title=f"Auto-Refresh Snapshot {index}", prompt_actions=False)

    def launch_gui(self) -> None:
        command = [sys.executable, "-m", "streamlit", "run", "news_aggregator/gui_streamlit.py"]
        self.console.print(f"[cyan]Launching GUI: {' '.join(command)}[/cyan]")
        try:
            subprocess.Popen(command, cwd=Path(__file__).resolve().parent.parent)
            self.console.print("[green]Streamlit GUI launched in a new process.[/green]")
        except FileNotFoundError:
            self.console.print("[bold red]Streamlit is not installed in the current environment.[/bold red]")

    def _display_results(self, articles: list[Article], *, title: str, prompt_actions: bool = True) -> None:
        self.last_results = articles
        if not articles:
            self.console.print(f"[yellow]No articles found for {title}.[/yellow]")
            return
        self.console.print(Panel.fit(f"[bold]{title}[/bold] - {len(articles)} articles"))
        self.console.print(build_article_table(articles))
        if prompt_actions:
            self._article_actions(articles)

    def _article_actions(self, articles: list[Article]) -> None:
        while True:
            action = Prompt.ask("Action", choices=["view", "bookmark", "back"], default="back")
            if action == "back":
                return
            index = IntPrompt.ask("Article number", default=1)
            if not (1 <= index <= len(articles)):
                self.console.print("[bold red]Invalid article selection.[/bold red]")
                continue
            article = articles[index - 1]
            if action == "view":
                self.console.print(build_article_panel(article))
            elif action == "bookmark":
                self.bookmarks.add(article)
                self.console.print(f"[green]Bookmarked:[/green] {article.title}")
                if not Confirm.ask("Bookmark another article", default=False):
                    return