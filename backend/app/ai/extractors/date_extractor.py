"""Extracts dates from raw document text using pattern matching.

Kept deliberately lightweight (regex, not a date-parsing library) since documents
come from wildly inconsistent sources -- certificates, letters, scanned OCR text --
and a strict parser would reject more than it accepts. Downstream consumers
(TimelineService) only need a year, so we favor recall over strict normalization.
"""

import re
from typing import Optional, List

MONTHS = (
    "January|February|March|April|May|June|July|"
    "August|September|October|November|December"
)


class DateExtractor:
    """Extracts a representative date string from document text."""

    PATTERNS = [
        r"\d{4}[-/]\d{1,2}[-/]\d{1,2}",             # 2024-03-15 or 2024/03/15
        rf"(?:{MONTHS})\s+\d{{1,2}},?\s+\d{{4}}",   # March 15, 2024
        rf"(?:{MONTHS})\s+\d{{4}}",                  # March 2024
        r"\d{1,2}[-/]\d{4}",                         # 03/2024
        r"\d{4}[-/]\d{1,2}",                         # 2024-03
        r"\d{4}",                                    # 2024 (fallback)
    ]

    def extract(self, text: str) -> Optional[str]:
        """Return the first date-like substring found, or None."""
        if not text:
            return None
        for pattern in self.PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def extract_all(self, text: str, limit: int = 10) -> List[str]:
        """Return every distinct date-like substring found (deduplicated, in order)."""
        if not text:
            return []
        found = []
        for pattern in self.PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                found.append(match.group(0))
        seen = []
        for f in found:
            if f not in seen:
                seen.append(f)
        return seen[:limit]


# Singleton instance
date_extractor = DateExtractor()
