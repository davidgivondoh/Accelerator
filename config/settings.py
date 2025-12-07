"""
Givondo Growth Engine - Configuration Settings

Uses Pydantic Settings for type-safe configuration with environment variable support.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ===========================================
    # API Keys
    # ===========================================
    google_api_key: SecretStr = Field(description="Google AI API key for Gemini")
    anthropic_api_key: SecretStr = Field(description="Anthropic API key for Claude")
    openai_api_key: SecretStr | None = Field(default=None, description="OpenAI API key (optional)")

    # ===========================================
    # Data Infrastructure
    # ===========================================
    database_url: SecretStr = Field(description="PostgreSQL connection string (Neon/local)")

    pinecone_api_key: SecretStr = Field(description="Pinecone API key")
    pinecone_environment: str = Field(default="us-east-1", description="Pinecone environment")
    pinecone_index: str = Field(default="growth-engine-embeddings", description="Pinecone index name")

    # ===========================================
    # GCP Settings
    # ===========================================
    google_cloud_project: str | None = Field(default=None, description="GCP project ID")
    google_cloud_region: str = Field(default="us-central1", description="GCP region")

    # ===========================================
    # Application Settings
    # ===========================================
    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="Application environment"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="Logging level"
    )

    # Daily quotas
    discovery_quota: int = Field(default=500, description="Max opportunities to discover per day")
    application_quota: int = Field(default=100, description="Max applications to generate per day")
    outreach_quota: int = Field(default=20, description="Max outreach messages per day")

    # ===========================================
    # Agent Configuration
    # ===========================================
    orchestrator_model: str = Field(default="gemini-2.0-flash-exp")
    discovery_model: str = Field(default="gemini-2.0-flash-exp")
    application_model: str = Field(default="claude-opus-4-5-20250514")
    profile_model: str = Field(default="gemini-1.5-pro")
    scoring_model: str = Field(default="gemini-1.5-flash")
    outreach_model: str = Field(default="gemini-2.0-flash-exp")

    # Temperature settings
    discovery_temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    application_temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    outreach_temperature: float = Field(default=0.6, ge=0.0, le=1.0)

    # ===========================================
    # Rate Limiting
    # ===========================================
    google_rpm: int = Field(default=60, description="Google API requests per minute")
    anthropic_rpm: int = Field(default=50, description="Anthropic API requests per minute")
    openai_rpm: int = Field(default=60, description="OpenAI API requests per minute")

    max_concurrent_discoveries: int = Field(default=10)
    max_concurrent_applications: int = Field(default=5)

    # ===========================================
    # Analytics (Optional)
    # ===========================================
    bigquery_dataset: str | None = Field(default=None)
    sentry_dsn: str | None = Field(default=None)

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience access
settings = get_settings()
