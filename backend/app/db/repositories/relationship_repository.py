"""Relationship-focused data access.

Narrow interface over the `relationships` table (edges connecting documents
to skills, and documents to each other) so relationship/graph-building code
doesn't need the full SQLiteDB surface area.
"""

from typing import Dict, List, Optional

from app.db.sqlite_db import sqlite_db


class RelationshipRepository:
    """Read/write access to the `relationships` table."""

    def __init__(self, db=None):
        self.db = db or sqlite_db

    def create(self, source_id: str, target_id: str, rel_type: str, weight: float = 1.0) -> str:
        return self.db.insert_relationship(source_id, target_id, rel_type, weight)

    def for_document(self, doc_id: str) -> List[Dict]:
        """All relationships where `doc_id` is either the source or the target."""
        return self.db.get_relationships(doc_id)

    def for_documents(self, doc_ids: List[str]) -> List[Dict]:
        """Aggregate, deduplicated relationships across multiple documents."""
        edges = []
        seen = set()
        for doc_id in doc_ids:
            for rel in self.db.get_relationships(doc_id):
                key = (rel["source_id"], rel["target_id"], rel["relationship_type"])
                if key in seen:
                    continue
                seen.add(key)
                edges.append(rel)
        return edges

    def upsert_skill(self, skill_name: str, category: Optional[str] = None) -> str:
        return self.db.upsert_skill(skill_name, category)

    def all_skills(self) -> List[Dict]:
        return self.db.get_all_skills()


# Singleton instance
relationship_repository = RelationshipRepository()
