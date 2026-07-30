from pydantic import BaseModel
from typing import List, Optional

class SearchQuery(BaseModel):
    """Natural language search query"""
    query: str
    filters: Optional[dict] = None
    limit: int = 10
    include_context: bool = True

class SearchResult(BaseModel):
    """Single search result"""
    document_id: str
    title: str
    category: str
    snippet: str
    similarity_score: float
    skills: List[str] = []
    date: Optional[str] = None
    highlights: List[str] = []

class SearchResponse(BaseModel):
    """Search response with results"""
    query: str
    total_results: int
    results: List[SearchResult]
    suggestions: List[str] = []
    processing_time_ms: float