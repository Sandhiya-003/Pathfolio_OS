"""
RETRIEVAL PIPELINE (RAG)
========================
Full Retrieval-Augmented workflow for natural language queries:

    ┌───────────┐   ┌──────────────┐   ┌──────────────┐   ┌───────────┐   ┌────────────┐
    │  "show my │──▶│    Intent     │──▶│   Semantic   │──▶│  Re-rank  │──▶│   Answer   │
    │AI projects"│   │  Detection   │   │Vector Search │   │ + Filter  │   │ Synthesis  │
    └───────────┘   └──────────────┘   └──────────────┘   └───────────┘   └────────────┘

Query understanding handles:
  - Category intent:  "show my CERTIFICATES"        → filter: certification
  - Skill intent:     "my PYTHON projects"          → boost: python
  - Temporal intent:  "LATEST resume", "2024 docs"  → sort/filter by date
  - Semantic intent:  everything else               → pure vector similarity
"""

import re
import time
from typing import Dict, List, Optional, Any

from app.services.vector_service import vector_service
from app.db.sqlite_db import sqlite_db
from app.core.config import settings
from app.core.logger import logger

# Intent detection vocabularies
CATEGORY_TRIGGERS = {
    "certification": ["certificate", "certificates", "certification", "certifications", "certified", "cert", "certs"],
    "project": ["project", "projects", "built", "developed", "portfolio piece"],
    "internship": ["internship", "internships", "intern", "work experience", "training"],
    "achievement": ["achievement", "achievements", "award", "awards", "won", "prize", "honor"],
    "academic": ["academic", "academics", "marksheet", "grade", "semester", "degree", "transcript"],
    "resume": ["resume", "resumes", "cv", "curriculum vitae"],
}

TEMPORAL_TRIGGERS = {
    "latest": ["latest", "newest", "most recent", "recent", "last"],
    "oldest": ["oldest", "first", "earliest"],
}


class RetrievalPipeline:
    """Natural-language document retrieval with query understanding."""

    def __init__(self):
        self.vector = vector_service
        self.db = sqlite_db

    # ══════════════════════════════════════════════
    # MAIN ENTRY: process a natural language query
    # ══════════════════════════════════════════════
    def run(self, query: str, user_id: str = "default_user", limit: int = 10) -> Dict[str, Any]:
        start = time.time()
        logger.info(f"🔍 [RAG] Query: '{query}'")

        # ── STAGE 1: Query Understanding ──
        intent = self._understand_query(query)
        logger.info(f"   🧠 Intent: {intent}")

        # ── STAGE 2: Semantic Retrieval ──
        filters = {"category": intent["category"]} if intent["category"] else None
        raw_results = self.vector.search(query=query, filters=filters, limit=limit * 2)

        # ── STAGE 3: Enrich + Re-rank ──
        ranked = self._rerank(raw_results, intent)

        # ── STAGE 4: Temporal handling ("latest resume") ──
        if intent["temporal"] == "latest":
            ranked.sort(key=lambda r: r.get("date") or "", reverse=True)
        elif intent["temporal"] == "oldest":
            ranked.sort(key=lambda r: r.get("date") or "9999")

        if intent["year"]:
            ranked = [r for r in ranked if intent["year"] in (r.get("date") or "")] or ranked

        final_results = ranked[:limit]

        # ── STAGE 5: Answer Synthesis ──
        answer = self._synthesize_answer(query, intent, final_results)

        elapsed_ms = round((time.time() - start) * 1000, 1)
        logger.info(f"   ✅ {len(final_results)} results in {elapsed_ms}ms")

        return {
            "query": query,
            "intent": intent,            # 👈 show this in UI: "AI understood: category=project, skill=python"
            "answer": answer,            # 👈 natural language summary above results
            "total_results": len(final_results),
            "results": final_results,
            "suggestions": self._suggestions(intent, final_results),
            "processing_time_ms": elapsed_ms,
        }

    # ─────────────────────────────────────────────
    # STAGE 1: Query Understanding
    # ─────────────────────────────────────────────
    def _understand_query(self, query: str) -> Dict[str, Any]:
        q = query.lower()

        # Detect category intent
        category = None
        for cat, triggers in CATEGORY_TRIGGERS.items():
            if any(t in q for t in triggers):
                category = cat
                break

        # Detect skill intent
        skills = [s for s in settings.SKILLS_KEYWORDS if re.search(rf"\b{re.escape(s)}\b", q)]

        # Detect temporal intent
        temporal = None
        for mode, triggers in TEMPORAL_TRIGGERS.items():
            if any(t in q for t in triggers):
                temporal = mode
                break

        # Detect year mentions ("from 2024")
        year_match = re.search(r"\b(20\d{2})\b", q)
        year = year_match.group(1) if year_match else None

        return {
            "category": category,
            "skills": skills,
            "temporal": temporal,
            "year": year,
            "is_broad": category is None and not skills,  # pure semantic query
        }

    # ─────────────────────────────────────────────
    # STAGE 3: Hybrid Re-ranking
    # ─────────────────────────────────────────────
    def _rerank(self, raw_results: List[Dict], intent: Dict) -> List[Dict]:
        """
        Hybrid scoring:  final = 0.7 * semantic_similarity + 0.3 * intent_boosts
        Boosts: exact skill match, category match, title keyword match.
        """
        enriched = []

        for r in raw_results:
            doc = self.db.get_document(r["id"])
            if not doc:
                continue

            semantic_score = r.get("similarity_score", 0)

            # Intent boosting
            boost = 0.0
            doc_skills = [s.lower() for s in doc.get("skills", [])]
            for skill in intent["skills"]:
                if skill.lower() in doc_skills:
                    boost += 0.5  # strong signal: exact skill match

            if intent["category"] and doc["category"] == intent["category"]:
                boost += 0.3

            final_score = 0.7 * semantic_score + 0.3 * min(boost, 1.0)

            enriched.append({
                "document_id": doc["id"],
                "title": doc["title"],
                "category": doc["category"],
                "snippet": doc.get("extracted_text", "")[:200] + "...",
                "similarity_score": round(semantic_score, 3),
                "final_score": round(final_score, 3),
                "skills": doc.get("skills", []),
                "date": doc.get("date_extracted"),
                "file_path": doc.get("file_path"),
                "original_filename": doc.get("original_filename"),
            })

        enriched.sort(key=lambda x: x["final_score"], reverse=True)
        return enriched

    # ─────────────────────────────────────────────
    # STAGE 5: Natural Language Answer Synthesis
    # ─────────────────────────────────────────────
    def _synthesize_answer(self, query: str, intent: Dict, results: List[Dict]) -> str:
        if not results:
            return "I couldn't find any documents matching that. Try uploading more documents or rephrasing your search."

        n = len(results)
        parts = []

        if intent["category"]:
            parts.append(f"Found {n} {intent['category']} document{'s' if n != 1 else ''}")
        else:
            parts.append(f"Found {n} relevant document{'s' if n != 1 else ''}")

        if intent["skills"]:
            parts.append(f"related to {', '.join(s.title() for s in intent['skills'])}")

        if intent["year"]:
            parts.append(f"from {intent['year']}")

        top = results[0]
        parts.append(f"— top match: '{top['title']}' ({top['final_score']:.0%} relevance)")

        return " ".join(parts) + "."

    def _suggestions(self, intent: Dict, results: List[Dict]) -> List[str]:
        suggestions = []
        if intent["skills"]:
            skill = intent["skills"][0].title()
            suggestions.append(f"Trace my {skill} journey over time")
        if intent["category"] == "certification":
            suggestions.append("Which projects used these certified skills?")
        if intent["category"] == "project":
            suggestions.append("Show certifications backing these projects")
        if results:
            cats = {r["category"] for r in results}
            for c in list(cats)[:2]:
                suggestions.append(f"Show all my {c}s")
        return list(dict.fromkeys(suggestions))[:3]  # dedupe, max 3


# Singleton instance
retrieval_pipeline = RetrievalPipeline()