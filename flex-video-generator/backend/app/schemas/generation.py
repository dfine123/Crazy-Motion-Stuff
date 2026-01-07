"""
Pydantic schemas for Generation model.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class GenerationStatus(str, Enum):
    """Generation status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ClipSequenceItem(BaseModel):
    """Schema for a clip in the sequence."""
    clip_id: UUID
    beat_segment: str = Field(..., description="intro|build|pre_drop|drop|sustain|outro")
    start_ms: int = Field(..., ge=0)
    end_ms: int = Field(..., ge=0)
    reasoning: Optional[str] = None


class CaptionMetadata(BaseModel):
    """Schema for caption metadata."""
    hook_type_used: Optional[str] = None
    estimated_length: Optional[int] = None
    cta_included: bool = False


class AIReasoning(BaseModel):
    """Schema for AI reasoning/debugging info."""
    clip_selection_reasoning: Optional[str] = None
    caption_reasoning: Optional[str] = None
    overall_strategy: Optional[str] = None


class GenerationCreate(BaseModel):
    """Schema for creating a Generation."""
    creator_id: UUID
    audio_id: UUID
    # Optional: manually specify clips (otherwise AI selects)
    clip_ids: Optional[list[UUID]] = None


class GenerationUpdate(BaseModel):
    """Schema for updating a Generation."""
    caption: Optional[str] = None
    status: Optional[GenerationStatus] = None


class GenerationResponse(BaseModel):
    """Schema for Generation response."""
    id: UUID
    creator_id: UUID
    audio_id: UUID
    clip_sequence: list[dict]
    caption: Optional[str]
    caption_metadata: dict
    ai_reasoning: dict
    output_path: Optional[str]
    status: str
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class GenerationListResponse(BaseModel):
    """Schema for list of Generations."""
    generations: list[GenerationResponse]
    total: int


class RegenerateCaptionRequest(BaseModel):
    """Schema for regenerating caption only."""
    keep_clips: bool = True


class RegenerateCaptionResponse(BaseModel):
    """Schema for caption regeneration response."""
    caption_options: list[dict]
    selected_caption: Optional[str] = None
