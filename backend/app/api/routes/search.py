from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from app.services.retrieval_service import retrieval_service
from app.core.logger import logger
from app.api.deps import get_current_user_id

router = APIRouter()

@router.get("/")
def search_documents(
    q: str = Query(..., min_length=1, description="Natural language search query"),
    category: Optional[str] = Query(None, description="Optional category filter"),
    limit: int = Query(10, ge=1, le=50),
    user_id: str = Depends(get_current_user_id),
):
    """
    Smart Retrieval: natural language search across the authenticated user's documents.
    Examples: "Show all my certificates", "Show my AI projects", "Show my latest resume"
    """
    try:
        filters = {"user_id": user_id}
        if category:
            filters["category"] = category
        return retrieval_service.search(query=q, filters=filters, limit=limit)
    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent")
def recent_documents(
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
):
    """Get the most recently added documents (used for the dashboard feed)"""
    try:
        docs = retrieval_service.get_recent_documents(user_id=user_id, limit=limit, category=category)
        return {"total": len(docs), "documents": docs}
    except Exception as e:
        logger.error(f"❌ Failed to fetch recent documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-skill/{skill}")
def documents_by_skill(skill: str, user_id: str = Depends(get_current_user_id)):
    """Find all of the authenticated user's documents connected to a specific skill"""
    try:
        docs = retrieval_service.get_documents_by_skill(skill, user_id=user_id)
        return {"skill": skill, "total": len(docs), "documents": docs}
    except Exception as e:
        logger.error(f"❌ Failed to fetch documents by skill: {e}")
        raise HTTPException(status_code=500, detail=str(e))
