"""Internal domain model for a relationship edge between two entities
(document<->skill, or document<->document)."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class RelationshipType(str, Enum):
    DOCUMENT_TO_SKILL = "document_to_skill"
    SIMILAR_DOCUMENT = "similar_document"
    SAME_CATEGORY = "same_category"
    SKILL_PROGRESSION = "skill_progression"


class RelationshipModel(BaseModel):
    id: Optional[str] = None
    source_id: str
    target_id: str
    relationship_type: str
    weight: float = 1.0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @property
    def is_skill_edge(self) -> bool:
        return self.target_id.startswith("skill_") or self.source_id.startswith("skill_")

    def involves(self, entity_id: str) -> bool:
        return entity_id in (self.source_id, self.target_id)

    def other_end(self, entity_id: str) -> Optional[str]:
        """Given one end of the edge, return the other end (or None if unrelated)."""
        if self.source_id == entity_id:
            return self.target_id
        if self.target_id == entity_id:
            return self.source_id
        return None
