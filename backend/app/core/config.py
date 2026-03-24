from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "World Geo Data API"
    APP_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/worldgeodata"
    )
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2")

    API_KEY_HEADER: str = "X-API-Key"
    RATE_LIMIT_PER_MINUTE: int = 120
    REQUEST_CACHE_TTL_SECONDS: int = 300

    CSC_BASE_URL: str = "https://countrystatecity.in"
    DR5HN_BASE_URL: str = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master"
    NIGERIA_LGA_DATASET_URL: str = (
        "https://raw.githubusercontent.com/temikeezy/nigeria-geojson-data/master/data/full.json"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
"""Application configuration."""
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API
    api_title: str = "World Geo Data API"
    api_version: str = "v1"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/worldgeodata"
    database_echo: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Security
    api_key_header: str = "X-API-Key"
    rate_limit_per_minute: int = 60

    # Environment
    environment: str = "development"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


settings = Settings()
