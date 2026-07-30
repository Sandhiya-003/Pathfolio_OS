from pydantic import BaseModel, Field
from typing import Optional, List

class UploadResponse(BaseModel):
    """Response after successful upload"""
    success: bool
    message: str
    document_id: str
    filename: str
    category: str
    skills_found: List[str] = []
    organizations_found: List[str] = []
    date_extracted: Optional[str] = None
    processing_time: float

class BatchUploadResponse(BaseModel):
    """Response for batch upload"""
    success: bool
    total_files: int
    successful: int
    failed: int
    documents: List[UploadResponse]
    errors: List[dict] = []