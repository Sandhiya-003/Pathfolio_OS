from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from app.services.timeline_service import timeline_service
from app.core.logger import logger
from app.api.deps import get_current_user_id

router = APIRouter()

@router.get("/")
def get_timeline(user_id: str = Depends(get_current_user_id)):
    """Get the complete journey timeline"""
    try:
        timeline = timeline_service.generate_timeline(user_id)
        return timeline
    except Exception as e:
        logger.error(f"❌ Failed to generate timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
def get_timeline_stats(user_id: str = Depends(get_current_user_id)):
    """Get timeline statistics"""
    try:
        stats = timeline_service.get_timeline_stats(user_id)
        return stats
    except Exception as e:
        logger.error(f"❌ Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/year/{year}")
def get_timeline_year(
    year: int,
    user_id: str = Depends(get_current_user_id)
):
    """Get events from a specific year"""
    try:
        timeline = timeline_service.generate_timeline(user_id)
        
        for year_data in timeline['timeline']:
            if year_data['year'] == year:
                return year_data
        
        raise HTTPException(status_code=404, detail=f"No events found for year {year}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get year timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/skills")
def get_skill_timeline(user_id: str = Depends(get_current_user_id)):
    """Get skill development over time"""
    try:
        timeline = timeline_service.generate_timeline(user_id)
        
        # Extract skills by year
        skills_by_year = {}
        for year_data in timeline['timeline']:
            year = year_data['year']
            year_skills = set()
            for event in year_data['events']:
                year_skills.update(event.get('skills', []))
            skills_by_year[year] = list(year_skills)
        
        return {
            "user_id": user_id,
            "skills_by_year": skills_by_year
        }
    except Exception as e:
        logger.error(f"❌ Failed to get skill timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))