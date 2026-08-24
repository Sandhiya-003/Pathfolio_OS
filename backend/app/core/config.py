from pydantic_settings import BaseSettings
from typing import List
import os


def _parse_origins(raw: str) -> List[str]:
    """Comma-separated env var -> list."""
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


class Settings(BaseSettings):
    """Application configuration settings."""

    # App Info
    APP_NAME: str = "PortfolioOS"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"

    # API Settings
    API_PREFIX: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = int(os.environ.get("PORT", "8000"))

    # CORS & Frontend URLs
    FRONTEND_URL: str = os.environ.get(
        "FRONTEND_URL",
        "http://localhost:5173"
    )

    ALLOWED_ORIGINS: str = os.environ.get(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174"
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        return _parse_origins(self.ALLOWED_ORIGINS)

    # Storage Paths
    BASE_DIR: str = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )

    UPLOAD_DIR: str = os.path.join(
        BASE_DIR,
        "app",
        "storage",
        "uploads"
    )

    PROCESSED_DIR: str = os.path.join(
        BASE_DIR,
        "app",
        "storage",
        "processed"
    )

    CHROMA_DB_DIR: str = os.path.join(
        BASE_DIR,
        "app",
        "storage",
        "chroma_db"
    )

    # Upload Limits
    MAX_UPLOAD_SIZE_MB: int = int(
        os.environ.get("MAX_UPLOAD_SIZE_MB", "20")
    )

    # AI / ML Settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    SIMILARITY_THRESHOLD: float = float(
        os.environ.get("SIMILARITY_THRESHOLD", "0.35")
    )
    MAX_SEARCH_RESULTS: int = 10

    # Document Categories
    CATEGORIES: List[str] = [
        "certification",
        "project",
        "internship",
        "achievement",
        "academic",
        "resume",
        "portfolio",
        "other"
    ]

    # Skills Keywords
    SKILLS_KEYWORDS: List[str] = [
        "python", "java", "javascript", "typescript", "react", "angular", "vue",
        "nodejs", "django", "flask", "fastapi", "spring", "express",
        "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
        "data science", "data analysis", "data engineering", "sql", "mongodb",
        "postgresql", "mysql", "firebase", "aws", "azure", "gcp", "docker",
        "kubernetes", "git", "github", "linux", "rest api", "graphql",
        "html", "css", "sass", "tailwind", "bootstrap",
        "nlp", "computer vision", "opencv", "pandas", "numpy", "scikit-learn",
        "excel", "tableau", "power bi", "statistics", "mathematics",
        "communication", "leadership", "teamwork", "problem solving"
    ]

    # Auth / JWT
    JWT_SECRET_KEY: str = os.environ.get(
        "JWT_SECRET_KEY",
        "dev-secret-change-me-in-production"
    )

    JWT_ALGORITHM: str = "HS256"

    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7

    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.environ.get(
        "GOOGLE_CLIENT_ID",
        ""
    )

    GOOGLE_CLIENT_SECRET: str = os.environ.get(
        "GOOGLE_CLIENT_SECRET",
        ""
    )

    GOOGLE_REDIRECT_URI: str = os.environ.get(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:8000/auth/google/callback"
    )

    # GitHub OAuth
    GITHUB_CLIENT_ID: str = os.environ.get(
        "GITHUB_CLIENT_ID",
        ""
    )

    GITHUB_CLIENT_SECRET: str = os.environ.get(
        "GITHUB_CLIENT_SECRET",
        ""
    )

    GITHUB_REDIRECT_URI: str = os.environ.get(
        "GITHUB_REDIRECT_URI",
        "http://localhost:8000/auth/github/callback"
    )

    # Gemini LLM
    GEMINI_API_KEY: str = os.environ.get(
        "GEMINI_API_KEY",
        ""
    )

    GEMINI_MODEL: str = os.environ.get(
        "GEMINI_MODEL",
        "gemini-3.7-flash"
    )

    GEMINI_MAX_TOKENS: int = 800
    GEMINI_TEMPERATURE: float = 0.3
    CHAT_CONTEXT_DOCS: int = 6

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
