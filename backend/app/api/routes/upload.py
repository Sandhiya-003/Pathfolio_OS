from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
from app.services.upload_service import upload_service
from app.db.sqlite_db import sqlite_db
from app.api.deps import get_current_user_id

router = APIRouter()
db = sqlite_db


@router.post("/single")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
):
    """Upload and process a single document"""
    return await upload_service.process(file, user_id)


@router.post("/batch")
async def upload_batch(
    files: List[UploadFile] = File(...),
    user_id: str = Depends(get_current_user_id),
):
    """Upload multiple documents at once"""
    results = []
    errors = []

    for file in files:
        try:
            result = await upload_service.process(file, user_id)
            results.append(result)
        except HTTPException as e:
            errors.append({"filename": file.filename, "error": e.detail})
        except Exception as e:
            errors.append({"filename": file.filename, "error": str(e)})

    successful = len([r for r in results if r.get('success', False)])

    return {
        "success": True,
        "total_files": len(files),
        "successful": successful,
        "failed": len(errors),
        "documents": results,
        "errors": errors
    }


@router.get("/stats")
def get_upload_stats(user_id: str = Depends(get_current_user_id)):
    """Get upload statistics"""
    stats = db.get_stats(user_id)
    return {
        "total_documents": stats['total_documents'],
        "documents_by_category": stats['by_category'],
        "skills_count": stats['skills_count']
    }
