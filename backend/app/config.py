"""
Application configuration.

Reads settings from environment variables / a local .env file via
pydantic-settings + python-dotenv. DATABASE_URL defaults to a local SQLite
file so the app runs with zero external services. Swapping to Postgres
(e.g. Supabase/Neon) later only requires changing DATABASE_URL -- no code
changes elsewhere, since SQLAlchemy's create_engine() dispatches on the URL
scheme and the ORM models avoid Postgres-only column types (the vector
embedding column is a stubbed Text/JSON column for now, see
app/models/system.py).
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "Egyptian Legal AI"
    ENV: str = "development"
    DEBUG: bool = True

    # --- Database ---
    # Default: local SQLite file, zero external services required.
    # Swap to e.g. postgresql+psycopg://user:pass@host:5432/db when ready
    # for Postgres + pgvector; no other code needs to change.
    DATABASE_URL: str = "sqlite:///./legal_ai.db"

    # --- Auth / JWT ---
    JWT_SECRET: str = "CHANGE_ME_DEV_SECRET_DO_NOT_USE_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # --- External APIs ---
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-flash-lite-latest"
    TAVILY_API_KEY: str = ""

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # --- Rate limiting (simple in-memory stub, see app/security/rate_limit.py) ---
    RATE_LIMIT_PER_MINUTE: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
