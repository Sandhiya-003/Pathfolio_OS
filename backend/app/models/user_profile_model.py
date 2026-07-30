"""Internal domain model representing a user's digital identity profile.

Broader than the account record in `users` (username/email/password) --
this aggregates account info with the archive stats that make up someone's
"digital identity": document counts, categories, and top skills. Used as a
typed shape for anything that wants to describe "this person" as a whole,
rather than just "this account."
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class UserProfileModel(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: Optional[datetime] = None

    total_documents: int = 0
    documents_by_category: Dict[str, int] = Field(default_factory=dict)
    top_skills: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True

    @property
    def strongest_category(self) -> Optional[str]:
        if not self.documents_by_category:
            return None
        return max(self.documents_by_category, key=self.documents_by_category.get)

    @property
    def is_new(self) -> bool:
        """True if the archive has fewer than 3 documents -- useful for onboarding UI."""
        return self.total_documents < 3

    @classmethod
    def from_user_and_stats(cls, user: dict, stats: dict, top_skills: List[str] = None) -> "UserProfileModel":
        """Build a profile from a raw `users` row plus a get_stats()-shaped dict."""
        return cls(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            full_name=user.get("full_name"),
            created_at=user.get("created_at"),
            total_documents=stats.get("total_documents", 0),
            documents_by_category=stats.get("by_category", {}),
            top_skills=top_skills or [],
        )
