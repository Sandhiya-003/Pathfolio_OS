"""Extracts known skills from document text via keyword matching.

Deliberately simple (word-boundary regex against a curated vocabulary in
settings.SKILLS_KEYWORDS) rather than a trained model -- for a personal document
archive, precision on a known skill list beats a noisy general-purpose extractor,
and it requires no additional model weights or GPU.
"""

import re
from typing import List

from app.core.config import settings


class SkillExtractor:
    """Extracts skills from text by matching against a known vocabulary."""

    def __init__(self, vocabulary: List[str] = None):
        self.vocabulary = vocabulary if vocabulary is not None else settings.SKILLS_KEYWORDS
        # Pre-compile patterns once so repeated calls don't re-parse regex each time
        self._patterns = [
            (skill, re.compile(r"\b" + re.escape(skill) + r"\b", re.IGNORECASE))
            for skill in self.vocabulary
        ]

    def extract(self, text: str) -> List[str]:
        """Return the deduplicated, title-cased list of skills found in `text`."""
        if not text:
            return []

        text_lower = text.lower()
        found = []
        for skill, pattern in self._patterns:
            if pattern.search(text_lower):
                found.append(skill.title())

        return list(dict.fromkeys(found))

    def score(self, text: str) -> dict:
        """Return {skill: occurrence_count} for skills found in `text`, most-mentioned first."""
        if not text:
            return {}

        text_lower = text.lower()
        counts = {}
        for skill, pattern in self._patterns:
            matches = pattern.findall(text_lower)
            if matches:
                counts[skill.title()] = len(matches)

        return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))


# Singleton instance
skill_extractor = SkillExtractor()
