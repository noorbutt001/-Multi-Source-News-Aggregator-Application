from __future__ import annotations

import asyncio
import io

import streamlit as st

from news_aggregator.config import CATEGORIES
from news_aggregator.services.aggregator import NewsAggregator
from news_aggregator.services.bookmarks import BookmarkService
from news_aggregator.services.exporters import export_to_csv, export_to_txt

st.set_page_config(page_title="News Aggregator", layout="wide")

aggregator = NewsAggregator()
bookmarks = BookmarkService()


async def _load_latest(category: str | None):
    return await aggregator.latest_news(category=category)


async def _load_search(query: str, category: str | None):
    return await aggregator.search_news(query=query, category=category)


st.title("🗞️ Multi-Source News Aggregator")
mode = st.sidebar.radio("Mode", ["Latest News", "Search News", "Bookmarks"])
category = st.sidebar.selectbox("Category", ["general", *CATEGORIES])
normalized_category = None if category == "general" else category


def _download_payload(file_type: str, articles):
    if file_type == "csv":
        path = export_to_csv(articles)
        mime = "text/csv"
    else:
        path = export_to_txt(articles)
        mime = "text/plain"
    with path.open("rb") as file:
        content = file.read()
    st.download_button(f"Download {file_type.upper()}", data=content, file_name=path.name, mime=mime)


if mode == "Latest News":
    if st.button("Fetch Latest News", type="primary"):
        st.session_state["articles"] = asyncio.run(_load_latest(normalized_category))
elif mode == "Search News":
    query = st.text_input("Keyword")
    if st.button("Search", type="primary") and query.strip():
        st.session_state["articles"] = asyncio.run(_load_search(query, normalized_category))
else:
    st.session_state["articles"] = bookmarks.list_bookmarks()

articles = st.session_state.get("articles", [])
if articles:
    for idx, article in enumerate(articles, start=1):
        with st.expander(f"{idx}. {article.title}"):
            st.write(f"**Source:** {article.source}")
            st.write(f"**Published:** {article.publication_label}")
            st.write(f"**Category:** {article.category.title()}")
            st.write(article.description or article.summary)
            st.write(article.summary)
            st.markdown(f"[Open article]({article.url})")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Bookmark {idx}", key=f"bookmark-{idx}"):
                    bookmarks.add(article)
                    st.success("Bookmarked")
            with col2:
                if mode == "Bookmarks" and st.button(f"Remove {idx}", key=f"remove-{idx}"):
                    bookmarks.remove(article.url)
                    st.rerun()
    _download_payload("csv", articles)
    _download_payload("txt", articles)
else:
    st.info("No articles loaded yet.")