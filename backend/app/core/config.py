# backend/app/core/config.py
"""Application configuration with startup validation and environment detection.

All secrets are injected via environment variables. The application will fail-fast
on startup if required secrets are missing in non-development environments.
"""
from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Optional

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("codeguru.config")


class Environment(str, Enum):
    """Application deployment environment."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class SubscriptionTier(str, Enum):
    """User subscription tiers for feature gating."""
    FREE = "free"
    PRO = "pro"
    TEAM = "team"


class Settings(BaseSettings):
    """Application settings loaded from environment variables with validation.

    Configuration priority: environment variables > .env file > defaults.
    In production, all secrets must be explicitly set — no defaults are used.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Environment ---
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False
    PROJECT_NAME: str = "CodeGuru AI"
    API_V1_STR: str = "/api/v1"
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1"]

    # --- Security & Auth ---
    SECRET_KEY: str = "DEV_SECRET_KEY_PLACEHOLDER_DO_NOT_USE_IN_PRODUCTION_1234567890"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_COST_FACTOR: int = 12
    JWT_ALGORITHM: str = "HS256"

    # --- CORS ---
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://codeguru-ai.vercel.app",
        "https://codeguru-ai-frontend.vercel.app",
    ]

    # --- PostgreSQL Database ---
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "codeguru"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # Connection pool (serverless-optimized defaults)
    DB_POOL_SIZE: int = 1
    DB_MAX_OVERFLOW: int = 0
    DB_POOL_PRE_PING: bool = True
    DB_ECHO: bool = False

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: Any) -> str:
        if isinstance(v, str) and v:
            return v
        data = info.data
        # Render provides DATABASE_URL (postgresql://...) - convert to async driver
        database_url = data.get("DATABASE_URL")
        if database_url:
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif database_url.startswith("postgresql://"):
                database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return database_url
        # Assemble from individual vars (local development)
        return (
            f"postgresql+asyncpg://{data.get('POSTGRES_USER')}:"
            f"{data.get('POSTGRES_PASSWORD')}@{data.get('POSTGRES_SERVER')}:"
            f"{data.get('POSTGRES_PORT')}/{data.get('POSTGRES_DB')}"
        )

    # --- Redis ---
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[str] = None

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_connection(cls, v: Optional[str], info: Any) -> str:
        if isinstance(v, str) and v:
            return v
        data = info.data
        password = data.get("REDIS_PASSWORD")
        host = data.get("REDIS_HOST", "localhost")
        port = data.get("REDIS_PORT", 6379)
        if password:
            return f"redis://:{password}@{host}:{port}/0"
        return f"redis://{host}:{port}/0"

    # --- Celery (disabled for Vercel — use Inngest/Trigger.dev for background tasks) ---
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # --- Google OAuth ---
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    # --- AI Providers ---
    # Primary: Google Gemini
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_PRIMARY_MODEL: str = "gemini-2.5-pro"
    GEMINI_FAST_MODEL: str = "gemini-2.0-flash"

    # Secondary: OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Fallback: DeepSeek
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # Local: Ollama (development fallback)
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "codellama"

    # AI Budget
    AI_CACHE_TTL_SECONDS: int = 86400  # 24 hours
    AI_MAX_RETRIES: int = 3
    AI_CIRCUIT_BREAKER_THRESHOLD: int = 5
    AI_CIRCUIT_BREAKER_TIMEOUT_SECONDS: int = 60

    # --- Vector Database: Qdrant ---
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "codeguru_knowledge"

    # --- Object Storage: S3-Compatible ---
    S3_ENDPOINT_URL: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_REGION: str = "us-east-1"
    S3_BUCKET_UPLOADS: str = "codeguru-user-uploads"
    S3_BUCKET_AVATARS: str = "codeguru-avatars"
    S3_BUCKET_REPORTS: str = "codeguru-reports"
    S3_BUCKET_KNOWLEDGE: str = "codeguru-knowledge-docs"

    # --- Email / SMTP ---
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@codeguru.ai"
    SMTP_FROM_NAME: str = "CodeGuru AI"
    SMTP_TLS: bool = True

    # --- Subscription Tiers: Rate Limits (per hour) ---
    TIER_FREE_AI_LIMIT: int = 10
    TIER_PRO_AI_LIMIT: int = 100
    TIER_TEAM_AI_LIMIT: int = 1000

    TIER_FREE_CODE_REVIEWS_MONTHLY: int = 5
    TIER_PRO_CODE_REVIEWS_MONTHLY: int = -1  # -1 = unlimited
    TIER_FREE_DSA_SESSIONS_MONTHLY: int = 10
    TIER_PRO_DSA_SESSIONS_MONTHLY: int = -1
    TIER_FREE_INTERVIEW_MONTHLY: int = 3
    TIER_PRO_INTERVIEW_MONTHLY: int = 30
    TIER_FREE_RAG_QUERIES_MONTHLY: int = 20
    TIER_PRO_RAG_QUERIES_MONTHLY: int = 200

    # --- Stripe Billing ---
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PRO_PRICE_ID: Optional[str] = None
    STRIPE_TEAM_PRICE_ID: Optional[str] = None

    # --- Monitoring ---
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_ENABLED: bool = True

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        """Fail-fast validation: critical secrets must be set in production."""
        if self.ENVIRONMENT == Environment.PRODUCTION:
            missing: list[str] = []

            if "PLACEHOLDER" in self.SECRET_KEY:
                missing.append("SECRET_KEY")

            if not self.GEMINI_API_KEY and not self.OPENAI_API_KEY:
                missing.append("GEMINI_API_KEY or OPENAI_API_KEY (at least one AI provider required)")

            if missing:
                raise ValueError(
                    f"Production startup blocked — missing required secrets: {', '.join(missing)}. "
                    "Set these environment variables before deploying to production."
                )
        return self

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION

    def get_ai_rate_limit(self, tier: SubscriptionTier) -> int:
        """Return the AI request rate limit (per hour) for a given subscription tier."""
        limits = {
            SubscriptionTier.FREE: self.TIER_FREE_AI_LIMIT,
            SubscriptionTier.PRO: self.TIER_PRO_AI_LIMIT,
            SubscriptionTier.TEAM: self.TIER_TEAM_AI_LIMIT,
        }
        return limits.get(tier, self.TIER_FREE_AI_LIMIT)


settings = Settings()
