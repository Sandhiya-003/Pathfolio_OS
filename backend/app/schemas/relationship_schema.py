from pydantic import BaseModel
from typing import List, Optional

class Node(BaseModel):
    """Graph node (document or skill)"""
    id: str
    label: str
    type: str  # "document" or "skill"
    category: Optional[str] = None
    size: float = 1.0

class Edge(BaseModel):
    """Connection between nodes"""
    source: str
    target: str
    type: str  # e.g., "certification_to_skill"
    weight: float

class RelationshipGraph(BaseModel):
    """Complete relationship graph"""
    nodes: List[Node]
    edges: List[Edge]

class RelationshipResponse(BaseModel):
    """Response with related documents"""
    document_id: str
    relationships: List[dict]
    skill_graph: RelationshipGraph