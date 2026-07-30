from fastapi import Header, HTTPException
from typing import Optional

from app.core.security import decode_access_token, TokenError
from app.db.sqlite_db import sqlite_db


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Resolve the authenticated user from the `Authorization: Bearer <token>` header.
    Raises 401 if the header is missing, malformed, or the token is invalid/expired.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.split(" ", 1)[1].strip()

    try:
        payload = decode_access_token(token)
    except TokenError as e:
        raise HTTPException(status_code=401, detail=str(e))

    user_id = payload.get("sub")
    user = sqlite_db.get_user_by_id(user_id) if user_id else None
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


async def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """Shortcut dependency: just the authenticated user's id."""
    user = await get_current_user(authorization)
    return user["id"]
