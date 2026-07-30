"""Lightweight extractive summarization.

Deliberately dependency-free (no transformer model) -- for short documents like
certificates and internship letters, a frequency-scored extractive summary is
fast, free, and good enough to give a document a human-readable one-line
description without adding another model to load at startup.
"""

import re
from typing import List

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "so", "of", "to", "in",
    "on", "for", "with", "as", "by", "at", "is", "are", "was", "were", "be",
    "been", "being", "this", "that", "these", "those", "it", "its", "from",
    "has", "have", "had", "will", "would", "could", "should", "can", "may",
    "i", "we", "you", "he", "she", "they", "them", "his", "her", "their",
    "not", "no", "do", "does", "did", "about", "into", "than", "which", "who",
}

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_WORD_RE = re.compile(r"[a-zA-Z]{2,}")


class SummarizationService:
    """Generates a short extractive summary from document text."""

    def _split_sentences(self, text: str) -> List[str]:
        cleaned = " ".join(text.split())  # normalize whitespace
        sentences = _SENTENCE_SPLIT.split(cleaned)
        return [s.strip() for s in sentences if len(s.strip()) > 0]

    def _word_frequencies(self, text: str) -> dict:
        words = [w.lower() for w in _WORD_RE.findall(text)]
        freqs = {}
        for w in words:
            if w in STOPWORDS:
                continue
            freqs[w] = freqs.get(w, 0) + 1
        if not freqs:
            return {}
        max_freq = max(freqs.values())
        return {w: count / max_freq for w, count in freqs.items()}

    def summarize(self, text: str, max_sentences: int = 2, max_chars: int = 240) -> str:
        """
        Produce a short extractive summary of `text`.

        Falls back to a truncated prefix of the text if there isn't enough
        content to meaningfully score sentences.
        """
        if not text or not text.strip():
            return ""

        sentences = self._split_sentences(text)
        if not sentences:
            return text[:max_chars].strip()

        if len(sentences) <= max_sentences:
            summary = " ".join(sentences)
            return summary[:max_chars].strip()

        freqs = self._word_frequencies(text)
        if not freqs:
            summary = " ".join(sentences[:max_sentences])
            return summary[:max_chars].strip()

        scored = []
        for idx, sentence in enumerate(sentences):
            words = [w.lower() for w in _WORD_RE.findall(sentence)]
            if not words:
                continue
            score = sum(freqs.get(w, 0) for w in words) / len(words)
            scored.append((idx, score, sentence))

        # Take the top-scoring sentences, then restore original reading order
        top = sorted(scored, key=lambda x: x[1], reverse=True)[:max_sentences]
        top_in_order = [s for s in sorted(top, key=lambda x: x[0])]

        summary = " ".join(s[2] for s in top_in_order)
        if len(summary) > max_chars:
            summary = summary[:max_chars].rsplit(" ", 1)[0] + "…"
        return summary.strip()


# Singleton instance
summarization_service = SummarizationService()
