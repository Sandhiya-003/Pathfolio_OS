from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: List[ChatMessage] = Field(default_factory=list, max_length=20)


class ChatSource(BaseModel):
    document_id: str
    title: str
    category: str
    date: Optional[str] = None
    similarity_score: float


class ChatResponse(BaseModel):
    answer: str
    sources: List[ChatSource]
    used_context: bool
    processing_time_ms: float
