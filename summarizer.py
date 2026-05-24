from __future__ import annotations

import re
from collections import Counter

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "in",
    "is", "it", "of", "on", "or", "that", "the", "to", "was", "were", "will", "with",
}


class BasicSummarizer:
    def summarize(self, text: str, max_sentences: int = 2) -> str:
        if not text.strip():
            return ""
        sentences = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", text) if segment.strip()]
        if len(sentences) <= max_sentences:
            return " ".join(sentences)

        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        frequencies = Counter(word for word in words if word not in STOPWORDS)
        if not frequencies:
            return " ".join(sentences[:max_sentences])

        scored: list[tuple[int, str]] = []
        for sentence in sentences:
            sentence_words = re.findall(r"\b[a-zA-Z]{3,}\b", sentence.lower())
            score = sum(frequencies.get(word, 0) for word in sentence_words)
            scored.append((score, sentence))

        top_sentences = {sentence for _, sentence in sorted(scored, reverse=True)[:max_sentences]}
        ordered = [sentence for sentence in sentences if sentence in top_sentences]
        return " ".join(ordered[:max_sentences])
    