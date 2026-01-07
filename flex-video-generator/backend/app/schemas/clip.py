"""
Pydantic schemas for Clip model.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ClipAnalysis(BaseModel):
    """Twelve Labs analysis result schema."""
    visual_content: Optional[str] = Field(None, description="Description of what's shown")
    detected_objects: list[str] = Field(default_factory=list)
    detected_actions: list[str] = Field(default_factory=list)
    detected_text: list[str] = Field(default_factory=list)
    scene_type: Optional[str] = Field(None, description="indoor|outdoor|aerial|pov|wide")
    dominant_colors: list[str] = Field(default_factory=list)
    has_faces: bool = False
    face_count: int = 0
    audio_content: Optional[str] = Field(None, description="ambient|music|speech|silent")


class ClipContext(BaseModel):
    """Manual/enhanced clip context schema."""
    flex_category: Optional[str] = Field(None, description="travel|cars|watches|lifestyle|money|property|experiences")
    flex_intensity: int = Field(3, ge=1, le=5)
    mood: Optional[str] = Field(None, description="aspirational|exclusive|casual|energetic|peaceful")
    best_for: list[str] = Field(default_factory=list, description="reveals|drops|intros|sustains|finales")
    avoid_pairing_with: list[str] = Field(default_factory=list)
    season: str = Field("any", description="summer|winter|spring|fall|any")
    location_type: Optional[str] = None
    custom_tags: list[str] = Field(default_factory=list)


class ClipTechnical(BaseModel):
    """Technical metadata schema."""
    orientation: str = Field("vertical", description="vertical|horizontal|square")
    resolution: Optional[str] = Field(None, description="e.g., 1080x1920")
    fps: int = Field(30, ge=1)
    has_audio: bool = False
    quality_score: int = Field(3, ge=1, le=5)


class ClipBase(BaseModel):
    """Base schema for Clip."""
    creator_id: UUID


class ClipCreate(ClipBase):
    """Schema for creating a Clip (file uploaded separately)."""
    context: ClipContext = Field(default_factory=ClipContext)
    technical: ClipTechnical = Field(default_factory=ClipTechnical)


class ClipUpdate(BaseModel):
    """Schema for updating a Clip."""
    context: Optional[ClipContext] = None
    technical: Optional[ClipTechnical] = None
    is_active: Optional[bool] = None


class ClipResponse(BaseModel):
    """Schema for Clip response."""
    id: UUID
    creator_id: UUID
    file_path: str
    thumbnail_path: Optional[str]
    duration_ms: int
    analysis: dict
    context: dict
    technical: dict
    twelve_labs_video_id: Optional[str]
    twelve_labs_index_id: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ClipListResponse(BaseModel):
    """Schema for list of Clips."""
    clips: list[ClipResponse]
    total: int


class ClipUploadResponse(BaseModel):
    """Schema for clip upload response."""
    clip_id: UUID
    file_path: str
    analysis_status: str  # pending|completed|error
    analysis: Optional[dict] = None
    error: Optional[str] = None
