from fastapi import APIRouter, HTTPException, Depends

from app.schemas.auth_schema import RegisterRequest, LoginRequest, TokenResponse, UserPublic
from app.services.auth_service import auth_service, AuthError
from app.api.deps import get_current_user
from app.core.logger import logger

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest):
    """Create a new account and return a bearer token."""
    try:
        user = auth_service.register(
            username=payload.username,
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
        )
    except AuthError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Registration failed: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

    token = auth_service.issue_token(user)
    return {"access_token": token, "user": user}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    """Authenticate with username/email + password and return a bearer token."""
    try:
        user = auth_service.authenticate(payload.identifier, payload.password)
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))

    token = auth_service.issue_token(user)
    return {"access_token": token, "user": user}


@router.get("/me", response_model=UserPublic)
def me(current_user: dict = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user