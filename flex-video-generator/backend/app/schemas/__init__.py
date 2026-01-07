"""
Pydantic schemas for API validation.
"""

from .creator import (
    CreatorCreate,
    CreatorUpdate,
    CreatorResponse,
    CreatorListResponse,
    BrandProfile,
    CaptionRules,
)
from .audio import (
    AudioTrackCreate,
    AudioTrackUpdate,
    AudioTrackResponse,
    AudioTrackListResponse,
    BeatTimestamp,
    AudioContext,
)
from .clip import (
    ClipCreate,
    ClipUpdate,
    ClipResponse,
    ClipListResponse,
    ClipAnalysis,
    ClipContext,
    ClipTechnical,
)
from .generation import (
    GenerationCreate,
    GenerationResponse,
    GenerationListResponse,
    ClipSequenceItem,
    GenerationStatus,
)
from .caption_profile import (
    CaptionProfileCreate,
    CaptionProfileUpdate,
    CaptionProfileResponse,
    CaptionProfileRules,
)

__all__ = [
    # Creator
    "CreatorCreate",
    "CreatorUpdate",
    "CreatorResponse",
    "CreatorListResponse",
    "BrandProfile",
    "CaptionRules",
    # Audio
    "AudioTrackCreate",
    "AudioTrackUpdate",
    "AudioTrackResponse",
    "AudioTrackListResponse",
    "BeatTimestamp",
    "AudioContext",
    # Clip
    "ClipCreate",
    "ClipUpdate",
    "ClipResponse",
    "ClipListResponse",
    "ClipAnalysis",
    "ClipContext",
    "ClipTechnical",
    # Generation
    "GenerationCreate",
    "GenerationResponse",
    "GenerationListResponse",
    "ClipSequenceItem",
    "GenerationStatus",
    # Caption Profile
    "CaptionProfileCreate",
    "CaptionProfileUpdate",
    "CaptionProfileResponse",
    "CaptionProfileRules",
]
