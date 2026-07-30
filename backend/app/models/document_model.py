"""Internal domain model for a stored document.

Distinct from `app/schemas/document_schema.py`, which defines the API
request/response shape. This model represents the document as an internal
object -- including fields (extracted_text, embedding_id) that are never
serialized back to the client -- and carries a couple of small computed
helpers used by services (year grouping, short previews).
"""

import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

_YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


class DocumentModel(BaseModel):
    id: str
    user_id: str
    title: str
    category: str
    file_type: str
    file_path: str
    original_filename: str
    extracted_text: str = ""
    skills: List[str] = Field(default_factory=list)
    organizations: List[str] = Field(default_factory=list)
    date_extracted: Optional[str] = None
    description: str = ""
    embedding_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @property
    def year(self) -> int:
        """Best-effort year this document belongs to, for timeline grouping."""
        source = self.date_extracted or (str(self.created_at) if self.created_at else "")
        match = _YEAR_RE.search(source)
        return int(match.group(0)) if match else datetime.now().year

    @property
    def preview(self) -> str:
        """A short plain-text preview of the extracted content."""
        text = " ".join(self.extracted_text.split())
        return text[:180] + ("…" if len(text) > 180 else "")

    def has_skill(self, skill: str) -> bool:
        return skill.lower() in [s.lower() for s in self.skills]

    def to_public_dict(self) -> dict:
        """Fields safe to return to the client (excludes raw extracted_text)."""
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "file_type": self.file_type,
            "original_filename": self.original_filename,
            "skills": self.skills,
            "organizations": self.organizations,
            "date_extracted": self.date_extracted,
            "description": self.description,
            "created_at": self.created_at,
        }
