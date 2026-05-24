import unittest

from news_aggregator.services.summarizer import BasicSummarizer


class TestBasicSummarizer(unittest.TestCase):
    def test_summarize_returns_top_sentences(self):
        text = (
            "AI is transforming newsrooms worldwide. "
            "Editors use automation to classify stories and detect duplicates. "
            "Some teams also generate summaries for faster reading. "
            "Weather forecasts remain unchanged."
        )
        summary = BasicSummarizer().summarize(text, max_sentences=2)
        self.assertIn("AI is transforming newsrooms worldwide.", summary)
        self.assertTrue(len(summary) > 10)


if __name__ == "__main__":
    unittest.main()