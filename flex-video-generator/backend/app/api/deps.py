"""
API dependencies for dependency injection.
"""

from typing import Generator
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.twelve_labs import TwelveLabsService
from app.services.claude_ai import ClaudeAIService
from app.services.video_engine import VideoEngine
from app.services.caption_gen import CaptionGenerator


def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_twelve_labs_service() -> TwelveLabsService:
    """Get Twelve Labs service instance."""
    return TwelveLabsService()


def get_claude_service() -> ClaudeAIService:
    """Get Claude AI service instance."""
    return ClaudeAIService()


def get_video_engine() -> VideoEngine:
    """Get video engine instance."""
    return VideoEngine()


def get_caption_generator() -> CaptionGenerator:
    """Get caption generator instance."""
    return CaptionGenerator()
