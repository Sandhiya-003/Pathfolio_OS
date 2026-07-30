from collections import Counter
from fastapi import APIRouter, HTTPException, Depends
from app.services.relationship_service import relationship_service
from app.db.sqlite_db import sqlite_db
from app.core.logger import logger
from app.api.deps import get_current_user_id

router = APIRouter()
db = sqlite_db


@router.get("/document/{doc_id}")
def get_document_relationships(doc_id: str, user_id: str = Depends(get_current_user_id)):
    """Get all relationships for a document owned by the authenticated user"""
    doc = db.get_document(doc_id)
    if not doc or doc.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        relationships = relationship_service.get_relationships(doc_id)
        related_docs = relationship_service.get_related_documents(doc_id)

        return {
            "document_id": doc_id,
            "relationships": relationships,
            "related_documents": related_docs
        }
    except Exception as e:
        logger.error(f"❌ Failed to get relationships: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/graph")
def get_relationship_graph(user_id: str = Depends(get_current_user_id)):
    """Get the authenticated user's skill-document relationship graph"""
    try:
        return relationship_service.get_skill_graph(user_id)
    except Exception as e:
        logger.error(f"❌ Failed to get graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/skills")
def get_all_skills(user_id: str = Depends(get_current_user_id)):
    """Get all skills (with document counts) drawn from the authenticated user's own documents"""
    try:
        documents = db.get_all_documents(user_id)
        counts = Counter()
        for doc in documents:
            for skill in doc.get("skills", []):
                counts[skill] += 1

        skills = [
            {"skill": skill, "document_count": count}
            for skill, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)
        ]

        return {
            "total_skills": len(skills),
            "skills": skills
        }
    except Exception as e:
        logger.error(f"❌ Failed to get skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/skills/{skill}")
def get_skill_details(skill: str, user_id: str = Depends(get_current_user_id)):
    """Get the authenticated user's documents matching a specific skill"""
    try:
        documents = db.get_all_documents(user_id)
        matching_docs = [
            doc for doc in documents
            if skill.lower() in [s.lower() for s in doc.get('skills', [])]
        ]

        return {
            "skill": skill,
            "document_count": len(matching_docs),
            "documents": matching_docs
        }
    except Exception as e:
        logger.error(f"❌ Failed to get skill details: {e}")
        raise HTTPException(status_code=500, detail=str(e))
