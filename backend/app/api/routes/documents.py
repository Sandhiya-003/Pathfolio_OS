import os
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import FileResponse
from typing import Optional
from app.db.sqlite_db import sqlite_db
from app.services.vector_service import vector_service
from app.core.logger import logger
from app.api.deps import get_current_user_id

router = APIRouter()
db = sqlite_db


def _get_owned_document(doc_id: str, user_id: str) -> dict:
    """Fetch a document and verify it belongs to the requesting user."""
    doc = db.get_document(doc_id)
    if not doc or doc.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/")
def list_documents(
    category: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    user_id: str = Depends(get_current_user_id),
):
    """List all documents for the authenticated user, optionally filtered by category."""
    try:
        if category:
            documents = db.get_documents_by_category(category, user_id)
        else:
            documents = db.get_all_documents(user_id)

        return {
            "total": len(documents),
            "documents": documents[:limit],
        }
    except Exception as e:
        logger.error(f"❌ Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
def get_document_stats(user_id: str = Depends(get_current_user_id)):
    """Get document statistics for the authenticated user"""
    try:
        stats = db.get_stats(user_id)
        return {
            "total_documents": stats["total_documents"],
            "documents_by_category": stats["by_category"],
            "skills_count": stats["skills_count"],
        }
    except Exception as e:
        logger.error(f"❌ Failed to get document stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{doc_id}")
def get_document(doc_id: str, user_id: str = Depends(get_current_user_id)):
    """Get full details for a single document (must be owned by the caller)"""
    return _get_owned_document(doc_id, user_id)

@router.get("/{doc_id}/download")
def download_document(doc_id: str, user_id: str = Depends(get_current_user_id)):
    """Download the original file, preserving its original format"""
    doc = _get_owned_document(doc_id, user_id)

    file_path = doc.get("file_path")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Original file is missing on disk")

    return FileResponse(
        path=file_path,
        filename=doc.get("original_filename") or os.path.basename(file_path),
    )
@router.delete("/{doc_id}")
def delete_document(doc_id: str, user_id: str = Depends(get_current_user_id)):
    """Delete a document and its associated file + vector embedding"""
    doc = _get_owned_document(doc_id, user_id)

    try:
        file_path = doc.get("file_path")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        vector_service.delete_document(doc_id)
        db.delete_relationships_for_document(doc_id)   # ← new line
        db.delete_document(doc_id)

        return {"success": True, "message": "Document deleted", "document_id": doc_id}
    except Exception as e:
        logger.error(f"❌ Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
