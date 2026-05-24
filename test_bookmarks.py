import tempfile
import unittest
from pathlib import Path

from news_aggregator.models import Article
from news_aggregator.services.bookmarks import BookmarkService


class TestBookmarkService(unittest.TestCase):
    def test_add_and_remove_bookmark(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            service = BookmarkService(Path(tmp_dir) / "bookmarks.json")
            article = Article(title="Test", source="Source", url="https://example.com")
            service.add(article)
            self.assertEqual(len(service.list_bookmarks()), 1)
            self.assertTrue(service.remove(article.url))
            self.assertEqual(len(service.list_bookmarks()), 0)


if __name__ == "__main__":
    unittest.main()