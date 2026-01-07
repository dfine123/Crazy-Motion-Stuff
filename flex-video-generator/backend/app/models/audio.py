"""
Audio track model for storing audio files with beat timestamps and context.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class AudioTrack(Base):
    """
    Audio track with beat timestamps, mood context, and pacing guides.

    context JSON structure:
    {
        "mood": "intense buildup|hype|chill|dramatic|motivational",
        "trend_type": "flex|motivation|reveal|transformation|lifestyle",
        "trend_origin": "TikTok original|remix|viral sound",
        "typical_use": "description of how this sound is typically used",
        "energy_arc": "build_drop|steady|escalating|peaks_valleys"
    }

    beat_timestamps JSON structure:
    [
        {
            "ms": 0,
            "type": "intro|build|pre_drop|drop|sustain|outro",
            "intensity": 1-5,
            "duration_ms": 3500,
            "notes": "subtle start, good for establishing shot",
            "recommended_clip_type": "lifestyle|flex|transition"
        },
        ...
    ]
    """

    __tablename__ = "audio_tracks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    duration_ms = Column(Integer, nullable=False)

    # Audio context (JSON)
    context = Column(JSONB, nullable=False, default=dict)

    # Beat timestamps (JSON array)
    beat_timestamps = Column(JSONB, nullable=False, default=list)

    # Pacing guide
    pacing_guide = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    generations = relationship("Generation", back_populates="audio")

    def __repr__(self) -> str:
        return f"<AudioTrack(id={self.id}, name='{self.name}', duration_ms={self.duration_ms})>"
