"""
Creator model for storing creator profiles with brand voice and style preferences.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class Creator(Base):
    """
    Creator profile with brand voice, style preferences, and content guidelines.

    brand_profile JSON structure:
    {
        "niche": "forex/crypto/ecom/motivation/lifestyle",
        "tone": ["confident", "luxurious", "aspirational"],
        "avoid": ["desperate language", "hype words", "clickbait"],
        "signature_phrases": ["string array of phrases they use"],
        "flex_style": "subtle|overt|educational",
        "lifestyle_themes": ["travel", "cars", "watches", "freedom", "family"]
    }

    caption_rules JSON structure:
    {
        "max_length": 150,
        "min_length": 50,
        "hashtag_strategy": "none|minimal|moderate",
        "hashtag_count": 3,
        "emoji_usage": "none|minimal|moderate",
        "cta_style": "soft|hard|none",
        "voice": "first_person|third_person",
        "banned_words": ["link in bio", "dm me"]
    }
    """

    __tablename__ = "creators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    handle = Column(String(100), nullable=True)

    # Brand voice profile (JSON)
    brand_profile = Column(JSONB, nullable=False, default=dict)

    # Caption rules (JSON)
    caption_rules = Column(JSONB, nullable=False, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    clips = relationship("Clip", back_populates="creator", cascade="all, delete-orphan")
    generations = relationship("Generation", back_populates="creator", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Creator(id={self.id}, name='{self.name}', handle='{self.handle}')>"
