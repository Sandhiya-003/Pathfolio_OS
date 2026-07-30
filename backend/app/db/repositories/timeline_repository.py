"""Timeline-focused data access.

There's no dedicated `timeline` table -- a user's timeline is derived from
their documents, sorted and grouped by date. This repository owns that raw
data-access concern (fetch + sort + group), leaving presentation concerns
(emojis, narrative summaries, per-year copy) to TimelineService.
"""

import re
from collections import defaultdict
from datetime import datetime
from typing import Dict, List

from app.db.sqlite_db import sqlite_db

_YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


class TimelineRepository:
    """Provides documents ordered and grouped chronologically for a user."""

    def __init__(self, db=None):
        self.db = db or sqlite_db

    def _year_of(self, document: Dict) -> int:
        date_str = document.get("date_extracted") or document.get("created_at") or ""
        match = _YEAR_RE.search(str(date_str))
        if match:
            return int(match.group(0))
        return datetime.now().year

    def documents_for_user(self, user_id: str) -> List[Dict]:
        """All of a user's documents, oldest first."""
        docs = self.db.get_all_documents(user_id)
        return sorted(docs, key=self._year_of)

    def documents_by_year(self, user_id: str) -> Dict[int, List[Dict]]:
        """A user's documents grouped by the year extracted from each one."""
        by_year = defaultdict(list)
        for doc in self.documents_for_user(user_id):
            by_year[self._year_of(doc)].append(doc)
        return dict(sorted(by_year.items()))

    def documents_for_year(self, user_id: str, year: int) -> List[Dict]:
        return self.documents_by_year(user_id).get(year, [])

    def year_range(self, user_id: str) -> tuple:
        """(earliest_year, latest_year) across a user's documents, or (None, None)."""
        years = list(self.documents_by_year(user_id).keys())
        if not years:
            return (None, None)
        return (min(years), max(years))


# Singleton instance
timeline_repository = TimelineRepository()
