from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas.insight_schema import InsightsResponse
from app.services.insight_service import insight_service
from app.core.logger import logger


router = APIRouter()


@router.get("/", response_model=InsightsResponse)
def get_all_insights(
    user_id: str = Query(
        "default_user",
        description="User whose insights should be generated"
    ),
    top_skills: int = Query(
        10,
        ge=1,
        le=50,
        description="Number of skills to return"
    ),
):
    """
    Return all dashboard insights.

    Endpoint:
    GET /api/insights/?user_id=default_user
    """

    try:
        return insight_service.get_dashboard_insights(
            user_id=user_id,
            top_skills=top_skills,
        )

    except Exception as exc:
        logger.exception("Failed to generate insights")
        raise HTTPException(
            status_code=500,
            detail=f"Could not generate insights: {str(exc)}",
        )


@router.get("/skills")
def get_skill_insights(
    user_id: str = "default_user",
    limit: int = Query(10, ge=1, le=100),
):
    """
    Return the user's strongest and most frequently evidenced skills.
    """

    try:
        skills = insight_service.get_skill_insights(
            user_id=user_id,
            limit=limit,
        )

        return {
            "user_id": user_id,
            "total": len(skills),
            "skills": skills,
        }

    except Exception as exc:
        logger.exception("Failed to generate skill insights")
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/skills/{skill_name}")
def get_skill_detail(
    skill_name: str,
    user_id: str = "default_user",
):
    """
    Return evidence for one skill.
    """

    try:
        result = insight_service.get_skill_detail(
            skill_name=skill_name,
            user_id=user_id,
        )

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No evidence found for skill '{skill_name}'",
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("Failed to get skill detail")
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/growth")
def get_growth_summary(
    user_id: str = "default_user",
):
    """
    Return the user's growth summary and yearly activity.
    """

    try:
        return insight_service.get_growth_summary(user_id=user_id)

    except Exception as exc:
        logger.exception("Failed to generate growth summary")
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/highlights")
def get_ai_highlights(
    user_id: str = "default_user",
):
    """
    Return automatically generated, evidence-based highlights.
    """

    try:
        highlights = insight_service.get_ai_highlights(user_id=user_id)

        return {
            "user_id": user_id,
            "highlights": highlights,
        }

    except Exception as exc:
        logger.exception("Failed to generate AI highlights")
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )