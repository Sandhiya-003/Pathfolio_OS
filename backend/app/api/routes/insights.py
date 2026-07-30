from fastapi import APIRouter, HTTPException, Depends
from app.services.insight_service import insight_service
from app.ai.pipelines.relationship_pipeline import relationship_pipeline
from app.core.logger import logger
from app.api.deps import get_current_user_id

router = APIRouter()

@router.get("/")
def get_insights(user_id: str = Depends(get_current_user_id)):
    """
    Get complete AI-generated career insights:
    profile score, skill strengths, gap analysis, growth metrics, highlights.
    """
    try:
        return insight_service.generate_insights(user_id)
    except Exception as e:
        logger.error(f"❌ Insights generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/skills")
def get_skill_insights(user_id: str = Depends(get_current_user_id)):
    """Get skill strength analysis only"""
    try:
        insights = insight_service.generate_insights(user_id)
        return {"skill_insights": insights["skill_insights"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gaps")
def get_skill_gaps(user_id: str = Depends(get_current_user_id)):
    """Get AI gap analysis — the career coach feature"""
    try:
        insights = insight_service.generate_insights(user_id)
        return {"skill_gaps": insights["skill_gaps"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/journey/{skill}")
def trace_skill_journey(skill: str, user_id: str = Depends(get_current_user_id)):
    """
    🎯 DEMO KILLER FEATURE:
    Trace how a skill evolved: Certification → Project → Internship
    """
    try:
        return relationship_pipeline.trace_journey(skill, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rebuild-graph")
def rebuild_knowledge_graph(user_id: str = Depends(get_current_user_id)):
    """Rebuild the full knowledge graph (run after batch uploads)"""
    try:
        return relationship_pipeline.rebuild_graph(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))