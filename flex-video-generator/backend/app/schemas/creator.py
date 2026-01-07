"""
Pydantic schemas for Creator model.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class BrandProfile(BaseModel):
    """Brand voice profile schema."""
    niche: Optional[str] = Field(None, description="forex/crypto/ecom/motivation/lifestyle")
    tone: list[str] = Field(default_factory=list, description="e.g., confident, luxurious, aspirational")
    avoid: list[str] = Field(default_factory=list, description="Words/phrases to avoid")
    signature_phrases: list[str] = Field(default_factory=list, description="Phrases the creator uses")
    flex_style: Optional[str] = Field(None, description="subtle|overt|educational")
    lifestyle_themes: list[str] = Field(default_factory=list, description="e.g., travel, cars, watches")


class CaptionRules(BaseModel):
    """Caption generation rules schema."""
    max_length: int = Field(150, ge=10, le=2200)
    min_length: int = Field(50, ge=1)
    hashtag_strategy: str = Field("minimal", description="none|minimal|moderate")
    hashtag_count: int = Field(3, ge=0, le=30)
    emoji_usage: str = Field("minimal", description="none|minimal|moderate")
    cta_style: str = Field("soft", description="soft|hard|none")
    voice: str = Field("first_person", description="first_person|third_person")
    banned_words: list[str] = Field(default_factory=list)


class CreatorBase(BaseModel):
    """Base schema for Creator."""
    name: str = Field(..., min_length=1, max_length=255)
    handle: Optional[str] = Field(None, max_length=100)


class CreatorCreate(CreatorBase):
    """Schema for creating a Creator."""
    brand_profile: BrandProfile = Field(default_factory=BrandProfile)
    caption_rules: CaptionRules = Field(default_factory=CaptionRules)


class CreatorUpdate(BaseModel):
    """Schema for updating a Creator."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    handle: Optional[str] = Field(None, max_length=100)
    brand_profile: Optional[BrandProfile] = None
    caption_rules: Optional[CaptionRules] = None


class CreatorResponse(CreatorBase):
    """Schema for Creator response."""
    id: UUID
    brand_profile: dict
    caption_rules: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreatorListResponse(BaseModel):
    """Schema for list of Creators."""
    creators: list[CreatorResponse]
    total: int
