from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DocumentCategory(str, Enum):
    CERTIFICATION = "certification"
    PROJECT = "project"
    INTERNSHIP = "internship"
    ACHIEVEMENT = "achievement"
    ACADEMIC = "academic"
    RESUME = "resume"
    PORTFOLIO = "portfolio"
    OTHER = "other"

class DocumentBase(BaseModel):
    """Base document schema"""
    title: str
    category: DocumentCategory
    file_type: str
    file_path: str
    original_filename: str

class DocumentCreate(DocumentBase):
    """Schema for creating a document"""
    user_id: Optional[str] = "default_user"
    extracted_text: str
    skills: List[str] = []
    organizations: List[str] = []
    date_extracted: Optional[str] = None
    description: Optional[str] = None
    embedding_id: Optional[str] = None

class DocumentResponse(DocumentBase):
    """Schema for document response"""
    id: str
    user_id: str
    extracted_text: str
    skills: List[str] = []
    organizations: List[str] = []
    date_extracted: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    """Schema for list of documents"""
    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int

class DocumentSummary(BaseModel):
    """Lightweight document info for search results"""
    id: str
    title: str
    category: str
    skills: List[str]
    date_extracted: Optional[str] = None
    similarity_score: Optional[float] = None