"""
Caption optimization profile model for storing reusable caption rules.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


class CaptionOptimizationProfile(Base):
    """
    Reusable caption optimization profile with hook patterns and rules.

    rules JSON structure:
    {
        "hook_patterns": [
            "Question that challenges viewer assumptions",
            "Controversial but defensible statement",
            "Specific number or result that creates curiosity",
            "POV setup that creates immersion",
            "This is what X looks like format"
        ],
        "structure": "hook → context → soft cta",
        "length_sweet_spot": {"min": 50, "max": 125, "ideal": 80},
        "formatting": {
            "line_breaks": "strategic|none|every_sentence",
            "capitalization": "normal|strategic_caps|all_lower"
        },
        "engagement_triggers": [
            "create curiosity gap",
            "imply exclusive knowledge",
            "challenge common beliefs",
            "promise transformation"
        ],
        "banned_patterns": [
            "click link",
            "dm me",
            "comment below",
            "follow for more",
            "link in bio"
        ],
        "trending_formats": [
            "This is what [X] looks like",
            "POV: you finally [X]",
            "The difference between [X] and [Y]",
            "[Number] years of [X] taught me [Y]"
        ]
    }
    """

    __tablename__ = "caption_optimization_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    is_default = Column(Boolean, default=False)

    # Optimization rules (JSON)
    rules = Column(JSONB, nullable=False, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<CaptionOptimizationProfile(id={self.id}, name='{self.name}', is_default={self.is_default})>"
