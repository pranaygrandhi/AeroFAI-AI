from pathlib import Path
from typing import List

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    secret_key: str = "CHANGE_ME"
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"

    database_url: PostgresDsn = "postgresql+asyncpg://user:password@localhost:5432/aerofai"
    redis_url: str = "redis://localhost:6379/0"

    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    s3_bucket: str = ""
    s3_region: str = ""

    class Config:
        env_file = Path(__file__).resolve().parents[2] / ".env"
        case_sensitive = False

    @field_validator("cors_origins", mode="before")
    def assemble_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
