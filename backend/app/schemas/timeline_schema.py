from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TimelineEvent(BaseModel):
    """Single event in the timeline"""
    id: str
    title: str
    category: str
    description: Optional[str] = None
    date: str
    year: int
    skills: List[str] = []
    document_id: str
    emoji: str

class TimelineYear(BaseModel):
    """Events grouped by year"""
    year: int
    events: List[TimelineEvent]
    summary: str

class TimelineResponse(BaseModel):
    """Complete timeline response"""
    user_id: str
    total_years: int
    total_events: int
    timeline: List[TimelineYear]
    generated_at: datetime

class TimelineStats(BaseModel):
    """Statistics about the timeline"""
    total_documents: int
    documents_by_category: dict
    skills_count: int
    top_skills: List[dict]
    career_growth_summary: str