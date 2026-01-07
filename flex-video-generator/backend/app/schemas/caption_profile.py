"""
Pydantic schemas for CaptionOptimizationProfile model.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class LengthSweetSpot(BaseModel):
    """Caption length preferences."""
    min: int = Field(50, ge=1)
    max: int = Field(125, ge=1)
    ideal: int = Field(80, ge=1)


class Formatting(BaseModel):
    """Caption formatting preferences."""
    line_breaks: str = Field("strategic", description="strategic|none|every_sentence")
    capitalization: str = Field("normal", description="normal|strategic_caps|all_lower")


class CaptionProfileRules(BaseModel):
    """Caption optimization rules schema."""
    hook_patterns: list[str] = Field(
        default_factory=lambda: [
            "Question that challenges viewer assumptions",
            "Controversial but defensible statement",
            "Specific number or result that creates curiosity",
            "POV setup that creates immersion",
            "This is what X looks like format"
        ]
    )
    structure: str = Field("hook → context → soft cta")
    length_sweet_spot: LengthSweetSpot = Field(default_factory=LengthSweetSpot)
    formatting: Formatting = Field(default_factory=Formatting)
    engagement_triggers: list[str] = Field(
        default_factory=lambda: [
            "create curiosity gap",
            "imply exclusive knowledge",
            "challenge common beliefs",
            "promise transformation"
        ]
    )
    banned_patterns: list[str] = Field(
        default_factory=lambda: [
            "click link",
            "dm me",
            "comment below",
            "follow for more",
            "link in bio"
        ]
    )
    trending_formats: list[str] = Field(
        default_factory=lambda: [
            "This is what [X] looks like",
            "POV: you finally [X]",
            "The difference between [X] and [Y]",
            "[Number] years of [X] taught me [Y]"
        ]
    )


class CaptionProfileBase(BaseModel):
    """Base schema for CaptionOptimizationProfile."""
    name: str = Field(..., min_length=1, max_length=255)


class CaptionProfileCreate(CaptionProfileBase):
    """Schema for creating a CaptionOptimizationProfile."""
    is_default: bool = False
    rules: CaptionProfileRules = Field(default_factory=CaptionProfileRules)


class CaptionProfileUpdate(BaseModel):
    """Schema for updating a CaptionOptimizationProfile."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_default: Optional[bool] = None
    rules: Optional[CaptionProfileRules] = None


class CaptionProfileResponse(CaptionProfileBase):
    """Schema for CaptionOptimizationProfile response."""
    id: UUID
    is_default: bool
    rules: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CaptionProfileListResponse(BaseModel):
    """Schema for list of CaptionOptimizationProfiles."""
    profiles: list[CaptionProfileResponse]
    total: int
