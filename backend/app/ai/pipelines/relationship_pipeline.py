"""
RELATIONSHIP PIPELINE
=====================
Builds the knowledge graph connecting a user's entire journey:

    Certification ──▶ Skill ──▶ Project ──▶ Internship ──▶ Career Path

Two AI strategies combined:
  1. SEMANTIC:  Cosine similarity between document embeddings (> 0.75 = connected)
  2. SYMBOLIC:  Rule-based domain logic (cert teaches skill, skill used in project...)

This hybrid neuro-symbolic approach is what separates this system
from simple "similar documents" features.
"""

import time
from typing import Dict, List, Any
from itertools import combinations

from app.services.embedding_service import embedding_service
from app.services.relationship_service import relationship_service
from app.db.sqlite_db import sqlite_db
from app.core.config import settings
from app.core.logger import logger

# The domain knowledge: which category naturally "flows into" which
CAREER_FLOW = {
    ("certification", "project"): {"type": "cert_applied_in_project", "weight": 0.9},
    ("academic", "project"): {"type": "academics_applied_in_project", "weight": 0.8},
    ("project", "internship"): {"type": "project_led_to_internship", "weight": 0.85},
    ("certification", "internship"): {"type": "cert_supported_internship", "weight": 0.8},
    ("internship", "achievement"): {"type": "internship_earned_achievement", "weight": 0.75},
    ("project", "achievement"): {"type": "project_earned_achievement", "weight": 0.75},
}


class RelationshipPipeline:
    """Builds & rebuilds the complete knowledge graph across all user documents."""

    def __init__(self):
        self.embedding = embedding_service
        self.relationships = relationship_service
        self.db = sqlite_db

    # ══════════════════════════════════════════════
    # FULL GRAPH REBUILD (run after batch uploads)
    # ══════════════════════════════════════════════
    def rebuild_graph(self, user_id: str = "default_user") -> Dict[str, Any]:
        """
        Rebuild ALL relationships from scratch using both
        semantic similarity and career-flow rules.
        """
        start = time.time()
        documents = self.db.get_all_documents(user_id)

        if len(documents) < 2:
            return {"success": True, "connections": 0, "message": "Need 2+ documents to build connections"}

        logger.info(f"🕸️ [GRAPH] Rebuilding knowledge graph for {len(documents)} documents...")

        semantic_edges = self._build_semantic_edges(documents)
        symbolic_edges = self._build_symbolic_edges(documents)
        skill_bridges = self._build_skill_bridges(documents)

        total = len(semantic_edges) + len(symbolic_edges) + len(skill_bridges)
        elapsed = round(time.time() - start, 2)

        logger.info(
            f"✅ [GRAPH] Built {total} connections in {elapsed}s "
            f"(semantic: {len(semantic_edges)}, career-flow: {len(symbolic_edges)}, "
            f"skill-bridges: {len(skill_bridges)})"
        )

        return {
            "success": True,
            "total_connections": total,
            "semantic_connections": len(semantic_edges),
            "career_flow_connections": len(symbolic_edges),
            "skill_bridge_connections": len(skill_bridges),
            "processing_time": elapsed,
        }

    # ─────────────────────────────────────────────
    # STRATEGY 1: Semantic edges (embedding cosine similarity)
    # ─────────────────────────────────────────────
    def _build_semantic_edges(self, documents: List[Dict]) -> List[str]:
        """Connect documents whose embeddings are highly similar."""
        edges = []
        texts = [
            f"{d['title']}. {' '.join(d.get('skills', []))}. {d.get('extracted_text', '')[:1000]}"
            for d in documents
        ]

        # Batch encode all documents at once (fast!)
        embeddings = self.embedding.encode(texts)

        # Compare every unique pair
        for i, j in combinations(range(len(documents)), 2):
            similarity = float(embeddings[i] @ embeddings[j])  # cosine (normalized vectors)

            if similarity >= settings.SIMILARITY_THRESHOLD:
                rel_id = self.db.insert_relationship(
                    source_id=documents[i]["id"],
                    target_id=documents[j]["id"],
                    rel_type="semantic_similarity",
                    weight=round(similarity, 3),
                )
                edges.append(rel_id)

        return edges

    # ─────────────────────────────────────────────
    # STRATEGY 2: Symbolic edges (career-flow rules)
    # ─────────────────────────────────────────────
    def _build_symbolic_edges(self, documents: List[Dict]) -> List[str]:
        """
        Apply domain rules: a certification and a project that share a skill
        are connected as "cert_applied_in_project", etc.
        """
        edges = []

        for i, j in combinations(range(len(documents)), 2):
            doc_a, doc_b = documents[i], documents[j]

            # Check both flow directions
            for (src, tgt), rule in CAREER_FLOW.items():
                pair = None
                if doc_a["category"] == src and doc_b["category"] == tgt:
                    pair = (doc_a, doc_b)
                elif doc_b["category"] == src and doc_a["category"] == tgt:
                    pair = (doc_b, doc_a)

                if pair:
                    # Only connect if they share at least one skill (evidence!)
                    skills_a = set(s.lower() for s in pair[0].get("skills", []))
                    skills_b = set(s.lower() for s in pair[1].get("skills", []))
                    shared = skills_a & skills_b

                    if shared:
                        rel_id = self.db.insert_relationship(
                            source_id=pair[0]["id"],
                            target_id=pair[1]["id"],
                            rel_type=rule["type"],
                            weight=rule["weight"],
                        )
                        edges.append(rel_id)

        return edges

    # ─────────────────────────────────────────────
    # STRATEGY 3: Skill bridges (document ↔ skill nodes)
    # ─────────────────────────────────────────────
    def _build_skill_bridges(self, documents: List[Dict]) -> List[str]:
        """Ensure every document is linked to its skill nodes."""
        edges = []
        for doc in documents:
            for skill in doc.get("skills", []):
                skill_id = self.db.upsert_skill(skill, doc["category"])
                rel_id = self.db.insert_relationship(
                    source_id=doc["id"],
                    target_id=f"skill_{skill_id}",
                    rel_type="document_to_skill",
                    weight=1.0,
                )
                edges.append(rel_id)
        return edges

    # ══════════════════════════════════════════════
    # JOURNEY PATH — the demo killer feature 🎯
    # ══════════════════════════════════════════════
    def trace_journey(self, skill: str, user_id: str = "default_user") -> Dict[str, Any]:
        """
        Trace a skill's complete journey through the user's career:

        "python" → Python Certification (2023)
                 → ML Stock Predictor Project (2024)
                 → Data Science Internship (2025)

        This answers: "How did I grow this skill over time?"
        """
        documents = self.db.get_all_documents(user_id)
        skill_lower = skill.lower()

        # Find all documents touching this skill
        related = [
            d for d in documents
            if skill_lower in [s.lower() for s in d.get("skills", [])]
        ]

        # Sort chronologically to show the growth story
        related.sort(key=lambda d: d.get("date_extracted") or d.get("created_at", ""))

        # Order path by career flow: academic → cert → project → internship → achievement
        flow_order = {"academic": 0, "certification": 1, "project": 2, "internship": 3, "achievement": 4}
        journey = sorted(related, key=lambda d: flow_order.get(d["category"], 5))

        path = [
            {
                "step": idx + 1,
                "document_id": d["id"],
                "title": d["title"],
                "category": d["category"],
                "date": d.get("date_extracted"),
                "narrative": self._narrate_step(d, skill),
            }
            for idx, d in enumerate(journey)
        ]

        return {
            "skill": skill,
            "journey_length": len(path),
            "path": path,
            "summary": self._narrate_journey(skill, path),
        }

    @staticmethod
    def _narrate_step(doc: Dict, skill: str) -> str:
        templates = {
            "academic": f"Studied {skill} fundamentals in '{doc['title']}'",
            "certification": f"Validated {skill} knowledge with '{doc['title']}'",
            "project": f"Applied {skill} hands-on in '{doc['title']}'",
            "internship": f"Used {skill} professionally at '{doc['title']}'",
            "achievement": f"Recognized for {skill} in '{doc['title']}'",
        }
        return templates.get(doc["category"], f"Worked with {skill} in '{doc['title']}'")

    @staticmethod
    def _narrate_journey(skill: str, path: List[Dict]) -> str:
        if not path:
            return f"No journey found for '{skill}' yet."
        if len(path) == 1:
            return f"Your {skill} journey has started with 1 milestone. Keep building!"
        return (
            f"Your {skill.title()} journey spans {len(path)} milestones — "
            f"from '{path[0]['title']}' to '{path[-1]['title']}'. "
            f"This shows clear skill progression from learning to application."
        )


# Singleton instance
relationship_pipeline = RelationshipPipeline()