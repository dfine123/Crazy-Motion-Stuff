"""
Clip model for storing video clips with Twelve Labs analysis and metadata.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class Clip(Base):
    """
    Video clip with Twelve Labs analysis and manual context.

    analysis JSON structure (from Twelve Labs):
    {
        "visual_content": "POV walking into private jet, leather interior visible",
        "detected_objects": ["private jet", "leather seats", "champagne"],
        "detected_actions": ["walking", "entering"],
        "detected_text": ["any text visible in clip"],
        "scene_type": "indoor|outdoor|aerial|pov|wide",
        "dominant_colors": ["#1a1a1a", "#d4af37"],
        "has_faces": true,
        "face_count": 1,
        "audio_content": "ambient|music|speech|silent"
    }

    context JSON structure (manual/enhanced):
    {
        "flex_category": "travel|cars|watches|lifestyle|money|property|experiences",
        "flex_intensity": 1-5,
        "mood": "aspirational|exclusive|casual|energetic|peaceful",
        "best_for": ["reveals", "drops", "intros", "sustains", "finales"],
        "avoid_pairing_with": ["casual clips", "low-energy moments"],
        "season": "summer|winter|spring|fall|any",
        "location_type": "private aviation|yacht|supercar|penthouse|beach|city",
        "custom_tags": ["user defined tags"]
    }

    technical JSON structure:
    {
        "orientation": "vertical|horizontal|square",
        "resolution": "1080x1920",
        "fps": 30,
        "has_audio": false,
        "quality_score": 1-5
    }
    """

    __tablename__ = "clips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("creators.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(500), nullable=False)
    thumbnail_path = Column(String(500), nullable=True)
    duration_ms = Column(Integer, nullable=False)

    # Twelve Labs analysis result (JSON)
    analysis = Column(JSONB, nullable=False, default=dict)

    # Manual/enhanced context (JSON)
    context = Column(JSONB, nullable=False, default=dict)

    # Technical metadata (JSON)
    technical = Column(JSONB, nullable=False, default=dict)

    # Twelve Labs IDs for re-querying
    twelve_labs_video_id = Column(String(100), nullable=True)
    twelve_labs_index_id = Column(String(100), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    creator = relationship("Creator", back_populates="clips")

    def __repr__(self) -> str:
        return f"<Clip(id={self.id}, creator_id={self.creator_id}, duration_ms={self.duration_ms})>"
