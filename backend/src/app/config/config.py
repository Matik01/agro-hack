from functools import lru_cache
from pathlib import Path
from pydantic import Field, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    APP_NAME: str = "AgroHack App"
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="development")

    YANDEX_API_KEY: str = Field(..., env="YANDEX_API_KEY")
    YANDEX_MODEL_URI: str = Field(..., env="YANDEX_MODEL_URI")
    GOOGLE_DRIVE_SCOPE: str = Field(..., env="GOOGLE_DRIVE_SCOPE")

    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    OUTPUT_DATA_FOLDER: str = 'data'


@lru_cache()
def get_settings() -> Settings:
    return Settings()