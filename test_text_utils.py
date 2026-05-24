import unittest
from datetime import datetime, timezone

from news_aggregator.models import Article
from news_aggregator.utils.text import deduplicate_articles, parse_datetime


class TestTextUtils(unittest.TestCase):
    def test_deduplicate_articles_removes_duplicates(self):
        first = Article(title="Breaking News", source="A", url="https://example.com/a")
        second = Article(title="Breaking   News", source="B", url="https://example.com/a")
        items = deduplicate_articles([first, second])
        self.assertEqual(len(items), 1)

    def test_parse_datetime_supports_rss_style_dates(self):
        parsed = parse_datetime("Tue, 14 May 2024 08:00:00 GMT")
        self.assertIsInstance(parsed, datetime)
        self.assertEqual(parsed.tzinfo, timezone.utc)


if __name__ == "__main__":
    unittest.main()