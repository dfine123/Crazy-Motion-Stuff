"""
Pydantic schemas for AudioTrack model.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class AudioContext(BaseModel):
    """Audio context schema."""
    mood: Optional[str] = Field(None, description="intense buildup|hype|chill|dramatic|motivational")
    trend_type: Optional[str] = Field(None, description="flex|motivation|reveal|transformation|lifestyle")
    trend_origin: Optional[str] = Field(None, description="TikTok original|remix|viral sound")
    typical_use: Optional[str] = Field(None, description="Description of how this sound is typically used")
    energy_arc: Optional[str] = Field(None, description="build_drop|steady|escalating|peaks_valleys")


class BeatTimestamp(BaseModel):
    """Beat timestamp schema."""
    ms: int = Field(..., ge=0, description="Timestamp in milliseconds")
    type: str = Field(..., description="intro|build|pre_drop|drop|sustain|outro")
    intensity: int = Field(3, ge=1, le=5, description="Intensity level 1-5")
    duration_ms: int = Field(3000, ge=100, description="Duration in milliseconds")
    notes: Optional[str] = Field(None, description="Notes about this beat segment")
    recommended_clip_type: Optional[str] = Field(None, description="lifestyle|flex|transition")


class AudioTrackBase(BaseModel):
    """Base schema for AudioTrack."""
    name: str = Field(..., min_length=1, max_length=255)


class AudioTrackCreate(AudioTrackBase):
    """Schema for creating an AudioTrack (file uploaded separately)."""
    context: AudioContext = Field(default_factory=AudioContext)
    pacing_guide: Optional[str] = None


class AudioTrackUpdate(BaseModel):
    """Schema for updating an AudioTrack."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    context: Optional[AudioContext] = None
    beat_timestamps: Optional[list[BeatTimestamp]] = None
    pacing_guide: Optional[str] = None
    is_active: Optional[bool] = None


class AudioTrackResponse(AudioTrackBase):
    """Schema for AudioTrack response."""
    id: UUID
    file_path: str
    duration_ms: int
    context: dict
    beat_timestamps: list[dict]
    pacing_guide: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AudioTrackListResponse(BaseModel):
    """Schema for list of AudioTracks."""
    audio_tracks: list[AudioTrackResponse]
    total: int
