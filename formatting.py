from __future__ import annotations

from rich.panel import Panel
from rich.table import Table

from news_aggregator.models import Article


def build_article_table(articles: list[Article]) -> Table:
    table = Table(show_lines=True, header_style="bold cyan")
    table.add_column("#", style="bold")
    table.add_column("Headline", overflow="fold")
    table.add_column("Source")
    table.add_column("Published")
    table.add_column("Category")
    table.add_column("Description", overflow="fold")

    for index, article in enumerate(articles, start=1):
        table.add_row(
            str(index),
            article.title,
            article.source,
            article.publication_label,
            article.category.title(),
            article.description or article.summary or "No description available",
        )
    return table


def build_article_panel(article: Article) -> Panel:
    body = (
        f"[bold]{article.title}[/bold]\n\n"
        f"[cyan]Source:[/cyan] {article.source}\n"
        f"[cyan]Published:[/cyan] {article.publication_label}\n"
        f"[cyan]Category:[/cyan] {article.category.title()}\n"
        f"[cyan]URL:[/cyan] {article.url}\n\n"
        f"[yellow]Description[/yellow]\n{article.description or 'No description available'}\n\n"
        f"[green]Summary[/green]\n{article.summary or 'No summary available'}"
    )
    return Panel(body, title="Article Detail", border_style="green")