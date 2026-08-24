"""
RETRIEVAL SERVICE
=================
Smart Retrieval (Module 5): natural-language search over a user's documents.

Two distinct paths, and this distinction matters a lot for correctness:

1. CATEGORY LISTING -- "show all my certificates", "show my resumes".
   These aren't really search queries, they're requests to LIST every
   document of a given type. Semantic/vector search is the wrong tool for
   this: it returns an approximate top-K by similarity, not "all of them",
   and generic category words ("resume", "certificate") don't reliably
   separate from each other in embedding space, so a resume query can
   easily surface a project report instead. For these, we detect the
   intent and go straight to a plain SQL category filter -- exact,
   complete, and fast.

2. EVERYTHING ELSE -- "AI projects", "leadership experience" -- genuine
   semantic search, where vector similarity is the right tool.
"""

import time
from collections import Counter
from typing import Dict, List, Optional

from app.db.sqlite_db import sqlite_db
from app.services.vector_service import vector_service
from app.core.constants import DOCUMENT_CATEGORIES
from app.core.logger import logger

# Maps a canonical category name to the words a user might actually type.
# Order matters only in that longer/more specific words should be checked
# first where there's overlap -- there isn't any meaningful overlap here.
CATEGORY_SYNONYMS = {
    "certification": ["certificate", "certificates", "certification", "certifications", "cert", "certs"],
    "project": ["project", "projects"],
    "internship": ["internship", "internships"],
    "achievement": ["achievement", "achievements", "award", "awards"],
    "academic": ["academic", "academics", "transcript", "transcripts", "marksheet", "marksheets"],
    "resume": ["resume", "resumes", "cv"],
    "portfolio": ["portfolio", "portfolios"],
}

# Only treat this as a "list this category" request if the query also looks
# like a listing request -- otherwise "how do I improve my resume" would
# incorrectly short-circuit into a plain category dump.
LISTING_TRIGGERS = ["show", "list", "view", "find", "get", "display", "all my", "my "]


class RetrievalService:
    """Handles natural-language search and retrieval over a user's documents."""

    def __init__(self):
        self.db = sqlite_db
        self.vector = vector_service

    # ------------------------------------------------------------------
    # Category-intent detection
    # ------------------------------------------------------------------

    def _detect_category_intent(self, query: str) -> Optional[str]:
        """Return a canonical category name if `query` looks like a request
        to list all documents of that type, else None."""
        q = query.lower().strip()

        looks_like_listing = any(trigger in q for trigger in LISTING_TRIGGERS)
        if not looks_like_listing:
            return None

        for category, synonyms in CATEGORY_SYNONYMS.items():
            for word in synonyms:
                if word in q:
                    return category
        return None

    def _list_by_category(self, category: str, user_id: str, query: str) -> Dict:
        """Exact SQL-backed listing of every document in a category -- used
        instead of semantic search when the query clearly wants "all of X"."""
        start_time = time.time()
        docs = self.db.get_documents_by_category(category, user_id)

        enriched_results = [
            {
                "document_id": d["id"],
                "title": d["title"],
                "category": d["category"],
                "snippet": self._generate_snippet(d.get("extracted_text", ""), query),
                "similarity_score": 1.0,  # exact category match, not an approximation
                "skills": d.get("skills", []),
                "date": d.get("date_extracted"),
                "highlights": [],
            }
            for d in docs
        ]

        processing_time = (time.time() - start_time) * 1000
        category_label = DOCUMENT_CATEGORIES.get(category, {}).get("label", category)

        return {
            "query": query,
            "total_results": len(enriched_results),
            "results": enriched_results,
            "suggestions": self._generate_suggestions(query, enriched_results),
            "low_confidence": False,
            "processing_time_ms": round(processing_time, 2),
        }

    # ------------------------------------------------------------------
    # Main search entrypoint
    # ------------------------------------------------------------------

    def search(self, query: str, filters: Dict = None, limit: int = 10) -> Dict:
        """
        Search a user's documents. Routes to exact category listing when the
        query looks like "show all my X"; otherwise does semantic search.
        """
        filters = dict(filters or {})
        user_id = filters.get("user_id")

        # Don't override an already-explicit category filter (e.g. the
        # frontend's category dropdown) with intent detection.
        if user_id and not filters.get("category"):
            detected_category = self._detect_category_intent(query)
            if detected_category:
                return self._list_by_category(detected_category, user_id, query)

        return self._semantic_search(query, filters, limit)

    def _semantic_search(self, query: str, filters: Dict, limit: int) -> Dict:
        start_time = time.time()

        search_results = self.vector.search(query, filters=filters, limit=limit)

        enriched_results = []
        for result in search_results:
            doc = self.db.get_document(result["id"])
            if doc:
                enriched_results.append({
                    "document_id": doc["id"],
                    "title": doc["title"],
                    "category": doc["category"],
                    "snippet": self._generate_snippet(doc.get("extracted_text", ""), query),
                    "similarity_score": result["similarity_score"],
                    "skills": doc.get("skills", []),
                    "date": doc.get("date_extracted"),
                    "highlights": self._generate_highlights(doc.get("extracted_text", ""), query),
                })

        low_confidence = bool(search_results) and search_results[0].get("low_confidence", False)
        processing_time = (time.time() - start_time) * 1000

        return {
            "query": query,
            "total_results": len(enriched_results),
            "results": enriched_results,
            "suggestions": self._generate_suggestions(query, enriched_results),
            "low_confidence": low_confidence,
            "processing_time_ms": round(processing_time, 2),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _generate_snippet(self, text: str, query: str, window: int = 220) -> str:
        """Return a short excerpt of `text`, centered on the first query
        term found, or the start of the document if nothing matches."""
        if not text:
            return ""

        text_lower = text.lower()
        query_words = [w for w in query.lower().split() if len(w) > 2]

        best_pos = None
        for word in query_words:
            pos = text_lower.find(word)
            if pos != -1 and (best_pos is None or pos < best_pos):
                best_pos = pos

        if best_pos is None:
            snippet = text[:window]
        else:
            start = max(0, best_pos - window // 3)
            snippet = text[start:start + window]

        snippet = " ".join(snippet.split())
        prefix = "…" if best_pos and best_pos > window // 3 else ""
        suffix = "…" if len(text) > window else ""
        return f"{prefix}{snippet}{suffix}"

    def _generate_highlights(self, text: str, query: str) -> List[str]:
        """Return the query terms that actually appear in `text`, for UI highlighting."""
        if not text:
            return []
        text_lower = text.lower()
        query_words = [w for w in query.lower().split() if len(w) > 2]
        return [w for w in query_words if w in text_lower]

    def _generate_suggestions(self, query: str, results: List[Dict]) -> List[str]:
        """
        Follow-up suggestions built from the ACTUAL results, not a static
        generic phrase -- a suggestion needs to be something semantic search
        (or category-intent detection) can actually match well when clicked.
        """
        if not results:
            return []

        suggestions = []

        all_skills = []
        for r in results:
            all_skills.extend(r.get("skills", []))
        top_skills = [s for s, _ in Counter(all_skills).most_common(2)]
        for skill in top_skills:
            suggestions.append(f"Show my {skill} documents")

        categories = list({r["category"] for r in results})
        for category in categories:
            if len(suggestions) >= 3:
                break
            suggestions.append(f"Show all my {category}s")

        return suggestions[:3]

    # ------------------------------------------------------------------
    # Used elsewhere (dashboard "recent", relationships "by skill")
    # ------------------------------------------------------------------

    def get_documents_by_skill(self, skill: str, user_id: str) -> List[Dict]:
        """Get all documents related to a specific skill, scoped to a user."""
        docs = self.db.get_all_documents(user_id)
        return [
            d for d in docs
            if skill.lower() in [s.lower() for s in d.get("skills", [])]
        ]

    def get_recent_documents(self, user_id: str, limit: int = 10, category: str = None) -> List[Dict]:
        """Get most recent documents for a user."""
        docs = self.db.get_all_documents(user_id)
        if category:
            docs = [d for d in docs if d["category"] == category]
        return docs[:limit]


# Singleton instance
retrieval_service = RetrievalService()