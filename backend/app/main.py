"""PortfolioOS backend entrypoint."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.api.routes import oauth as oauth_routes
from app.core.config import settings
from app.core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    for directory in (
        settings.UPLOAD_DIR,
        settings.PROCESSED_DIR,
        settings.CHROMA_DB_DIR,
    ):
        os.makedirs(directory, exist_ok=True)

    logger.info(f"🚀 {settings.APP_NAME} v{settings.VERSION} starting up")

    if settings.JWT_SECRET_KEY == "dev-secret-change-me-in-production":
        if settings.DEBUG:
            logger.warning(
                "⚠️  Using the default JWT_SECRET_KEY. Fine for local dev, "
                "but set a real one in .env before deploying."
            )
        else:
            logger.error(
                "❌ DEBUG=false but JWT_SECRET_KEY is still the default dev value. "
                "Set a real JWT_SECRET_KEY in your environment before exposing this "
                "publicly -- anyone can forge login tokens otherwise."
            )

    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        logger.warning("⚠️  GOOGLE_CLIENT_ID/SECRET not set -- Google sign-in will fail if used.")
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        logger.warning("⚠️  GITHUB_CLIENT_ID/SECRET not set -- GitHub sign-in will fail if used.")

    try:
        from app.db.sqlite_db import sqlite_db  # noqa: F401
        from app.db.chroma_db import chroma_client  # noqa: F401

        logger.info("✅ Databases initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize databases: {e}")
        raise

    yield

    logger.info(f"👋 {settings.APP_NAME} shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for the PortfolioOS portfolio platform.",
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# All local API routes (auth register/login/me, upload, search, documents,
# timeline, relationships, insights, chat) live under /api.
app.include_router(api_router, prefix=settings.API_PREFIX)

# OAuth routes are mounted separately, directly on the app, at the root
# /auth/... path -- NOT under /api. This must exactly match GOOGLE_REDIRECT_URI
# / GITHUB_REDIRECT_URI in your .env and in the Google/GitHub app consoles
# (default: http://localhost:8000/auth/google/callback, .../auth/github/callback).
app.include_router(oauth_routes.router, prefix="/auth")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"❌ HTTP {exc.status_code} on {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"❌ Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"success": False, "error": "Validation failed", "details": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Unhandled error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"},
    )


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.VERSION,
        "docs": "/docs",
        "api_prefix": settings.API_PREFIX,
    }


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.VERSION}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )