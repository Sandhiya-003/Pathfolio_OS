from fastapi import APIRouter, HTTPException, Depends

from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.chat_service import chat_service, ChatServiceError
from app.api.deps import get_current_user_id
from app.core.logger import logger

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def ask_assistant(payload: ChatRequest, user_id: str = Depends(get_current_user_id)):
    """
    Ask a natural-language question about your archive. Retrieves relevant
    documents (scoped to the authenticated user) and answers using Groq,
    citing which documents it drew from.
    """
    history = [turn.model_dump() for turn in payload.history]

    try:
        return chat_service.ask(payload.message, user_id=user_id, history=history)
    except ChatServiceError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Chat failed: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong answering that.")
