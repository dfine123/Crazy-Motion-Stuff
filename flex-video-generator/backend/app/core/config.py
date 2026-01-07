"""
Application configuration using Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from pathlib import Path
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql://flexgen:flexgen_secret@localhost:5432/flex_generator"

    # API Keys
    anthropic_api_key: str = ""
    twelve_labs_api_key: str = ""

    # Storage paths
    storage_root: str = "/storage"
    audio_path: str = "/storage/audio"
    clips_path: str = "/storage/clips"
    exports_path: str = "/storage/exports"
    temp_path: str = "/storage/temp"

    # Server
    backend_port: int = 8000
    frontend_port: int = 3000

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Claude model
    claude_model: str = "claude-sonnet-4-20250514"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def ensure_directories(self) -> None:
        """Create storage directories if they don't exist."""
        for path in [self.audio_path, self.clips_path, self.exports_path, self.temp_path]:
            Path(path).mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.ensure_directories()
    return settings
