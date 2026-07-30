"""Re-exports the service singletons that already live in each submodule.

Each service module creates its own singleton at import time (e.g.
`embedding_service = EmbeddingService()` at the bottom of embedding_service.py).
This file just re-exports those same instances for `from app.services import x`
style imports -- it must NOT construct new instances, or heavy models
(the sentence-transformer, spaCy) end up loaded twice at startup.
"""

from app.services.embedding_service import embedding_service
from app.services.extraction_service import extraction_service
from app.services.classification_service import classification_service
from app.services.vector_service import vector_service
from app.services.relationship_service import relationship_service
from app.services.timeline_service import timeline_service
from app.services.retrieval_service import retrieval_service
from app.services.insight_service import insight_service
from app.services.upload_service import upload_service
from app.services.auth_service import auth_service
from app.services.summarization_service import summarization_service
from app.services.parser_service import parser_service
from app.services.chat_service import chat_service

__all__ = [
    "embedding_service",
    "extraction_service",
    "classification_service",
    "vector_service",
    "relationship_service",
    "timeline_service",
    "retrieval_service",
    "insight_service",
    "upload_service",
    "auth_service",
    "summarization_service",
    "parser_service",
    "chat_service",
]
