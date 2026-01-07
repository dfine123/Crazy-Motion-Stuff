"""
Settings and configuration API routes.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.caption_profile import CaptionOptimizationProfile
from app.schemas.caption_profile import (
    CaptionProfileCreate,
    CaptionProfileUpdate,
    CaptionProfileResponse,
    CaptionProfileListResponse,
)
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("")
def get_settings_info():
    """Get application settings (non-sensitive)."""
    return {
        "storage_root": settings.storage_root,
        "audio_path": settings.audio_path,
        "clips_path": settings.clips_path,
        "exports_path": settings.exports_path,
        "claude_model": settings.claude_model,
        "api_configured": {
            "anthropic": bool(settings.anthropic_api_key),
            "twelve_labs": bool(settings.twelve_labs_api_key),
        }
    }


@router.get("/caption-profiles", response_model=CaptionProfileListResponse)
def list_caption_profiles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all caption optimization profiles."""
    query = db.query(CaptionOptimizationProfile)
    total = query.count()
    profiles = query.offset(skip).limit(limit).all()

    return CaptionProfileListResponse(profiles=profiles, total=total)


@router.post("/caption-profiles", response_model=CaptionProfileResponse, status_code=status.HTTP_201_CREATED)
def create_caption_profile(
    profile_in: CaptionProfileCreate,
    db: Session = Depends(get_db)
):
    """Create a new caption optimization profile."""
    # If this is set as default, unset others
    if profile_in.is_default:
        db.query(CaptionOptimizationProfile).filter(
            CaptionOptimizationProfile.is_default == True
        ).update({"is_default": False})

    profile = CaptionOptimizationProfile(
        name=profile_in.name,
        is_default=profile_in.is_default,
        rules=profile_in.rules.model_dump(),
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/caption-profiles/default", response_model=CaptionProfileResponse)
def get_default_caption_profile(
    db: Session = Depends(get_db)
):
    """Get the default caption optimization profile."""
    profile = db.query(CaptionOptimizationProfile).filter(
        CaptionOptimizationProfile.is_default == True
    ).first()

    if not profile:
        # Create default profile if none exists
        from app.schemas.caption_profile import CaptionProfileRules
        default_rules = CaptionProfileRules()

        profile = CaptionOptimizationProfile(
            name="Default",
            is_default=True,
            rules=default_rules.model_dump(),
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return profile


@router.get("/caption-profiles/{profile_id}", response_model=CaptionProfileResponse)
def get_caption_profile(
    profile_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific caption profile by ID."""
    profile = db.query(CaptionOptimizationProfile).filter(
        CaptionOptimizationProfile.id == profile_id
    ).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caption profile not found"
        )
    return profile


@router.put("/caption-profiles/{profile_id}", response_model=CaptionProfileResponse)
def update_caption_profile(
    profile_id: UUID,
    profile_in: CaptionProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update a caption optimization profile."""
    profile = db.query(CaptionOptimizationProfile).filter(
        CaptionOptimizationProfile.id == profile_id
    ).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caption profile not found"
        )

    update_data = profile_in.model_dump(exclude_unset=True)

    # Handle is_default change
    if update_data.get("is_default"):
        db.query(CaptionOptimizationProfile).filter(
            CaptionOptimizationProfile.is_default == True,
            CaptionOptimizationProfile.id != profile_id
        ).update({"is_default": False})

    # Handle nested rules
    if "rules" in update_data and update_data["rules"]:
        update_data["rules"] = update_data["rules"].model_dump() if hasattr(update_data["rules"], 'model_dump') else update_data["rules"]

    for field, value in update_data.items():
        if value is not None:
            setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/caption-profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_caption_profile(
    profile_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a caption optimization profile."""
    profile = db.query(CaptionOptimizationProfile).filter(
        CaptionOptimizationProfile.id == profile_id
    ).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caption profile not found"
        )

    if profile.is_default:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete default profile. Set another profile as default first."
        )

    db.delete(profile)
    db.commit()
    return None


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
