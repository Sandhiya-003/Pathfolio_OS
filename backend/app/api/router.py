from fastapi import APIRouter
from app.api.routes import auth, upload, search, documents, timeline, relationships, insights, chat

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(upload.router, prefix="/upload", tags=["Upload"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(timeline.router, prefix="/timeline", tags=["Timeline"])
api_router.include_router(relationships.router, prefix="/relationships", tags=["Relationships"])
api_router.include_router(insights.router, prefix="/insights", tags=["Insights"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])