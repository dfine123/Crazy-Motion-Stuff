"""
Generation model for tracking video generation jobs and history.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class Generation(Base):
    """
    Video generation job with clip sequence, caption, and rendering status.

    clip_sequence JSON structure:
    [
        {"clip_id": "uuid", "start_ms": 0, "end_ms": 3500, "beat_segment": "intro"},
        ...
    ]

    caption_metadata JSON structure:
    {
        "hook_type_used": "which hook pattern",
        "estimated_length": 85,
        "cta_included": true
    }

    ai_reasoning JSON structure:
    {
        "clip_selection_reasoning": "...",
        "caption_reasoning": "...",
        "overall_strategy": "..."
    }
    """

    __tablename__ = "generations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("creators.id"), nullable=False)
    audio_id = Column(UUID(as_uuid=True), ForeignKey("audio_tracks.id"), nullable=False)

    # Selected clips in order
    clip_sequence = Column(JSONB, nullable=False, default=list)

    # Generated caption
    caption = Column(Text, nullable=True)
    caption_metadata = Column(JSONB, default=dict)

    # AI reasoning (for debugging/improvement)
    ai_reasoning = Column(JSONB, default=dict)

    # Output
    output_path = Column(String(500), nullable=True)

    # Status: pending, processing, completed, failed
    status = Column(String(50), default="pending")
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    creator = relationship("Creator", back_populates="generations")
    audio = relationship("AudioTrack", back_populates="generations")

    def __repr__(self) -> str:
        return f"<Generation(id={self.id}, status='{self.status}', creator_id={self.creator_id})>"
