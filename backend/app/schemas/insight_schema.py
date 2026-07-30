from pydantic import BaseModel
from typing import List, Optional, Dict

class SkillInsight(BaseModel):
    """Analysis of a single skill"""
    skill: str
    document_count: int
    categories: List[str]          # where this skill appears
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    strength: str                  # "emerging" | "developing" | "strong"
    evidence: List[str] = []       # document titles proving the skill

class SkillGap(BaseModel):
    """A detected gap in the user's profile"""
    gap_type: str                  # e.g. "skill_without_certification"
    title: str
    description: str
    recommendation: str
    priority: str                  # "high" | "medium" | "low"

class GrowthMetric(BaseModel):
    """Year-over-year growth data"""
    year: int
    documents_added: int
    new_skills: List[str]
    categories_touched: List[str]

class ProfileScore(BaseModel):
    """Overall profile completeness score"""
    overall_score: int             # 0-100
    breakdown: Dict[str, int]      # per-dimension scores
    level: str                     # "Beginner" | "Builder" | "Achiever" | "Professional"

class AIHighlight(BaseModel):
    """An AI-generated highlight about the user"""
    icon: str
    title: str
    detail: str
    highlight_type: str            # "strength" | "milestone" | "trend" | "gap"

class InsightsResponse(BaseModel):
    """Complete insights payload"""
    profile_score: ProfileScore
    skill_insights: List[SkillInsight]
    skill_gaps: List[SkillGap]
    growth_metrics: List[GrowthMetric]
    highlights: List[AIHighlight]
    generated_at: str