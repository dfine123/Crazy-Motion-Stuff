"""
Creator management API routes.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.creator import Creator
from app.schemas.creator import (
    CreatorCreate,
    CreatorUpdate,
    CreatorResponse,
    CreatorListResponse,
)

router = APIRouter()


@router.post("", response_model=CreatorResponse, status_code=status.HTTP_201_CREATED)
def create_creator(
    creator_in: CreatorCreate,
    db: Session = Depends(get_db)
):
    """Create a new creator profile."""
    creator = Creator(
        name=creator_in.name,
        handle=creator_in.handle,
        brand_profile=creator_in.brand_profile.model_dump(),
        caption_rules=creator_in.caption_rules.model_dump(),
    )
    db.add(creator)
    db.commit()
    db.refresh(creator)
    return creator


@router.get("", response_model=CreatorListResponse)
def list_creators(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all creators with optional search."""
    query = db.query(Creator)

    if search:
        query = query.filter(
            Creator.name.ilike(f"%{search}%") |
            Creator.handle.ilike(f"%{search}%")
        )

    total = query.count()
    creators = query.offset(skip).limit(limit).all()

    return CreatorListResponse(creators=creators, total=total)


@router.get("/{creator_id}", response_model=CreatorResponse)
def get_creator(
    creator_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific creator by ID."""
    creator = db.query(Creator).filter(Creator.id == creator_id).first()
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator not found"
        )
    return creator


@router.put("/{creator_id}", response_model=CreatorResponse)
def update_creator(
    creator_id: UUID,
    creator_in: CreatorUpdate,
    db: Session = Depends(get_db)
):
    """Update a creator profile."""
    creator = db.query(Creator).filter(Creator.id == creator_id).first()
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator not found"
        )

    update_data = creator_in.model_dump(exclude_unset=True)

    # Handle nested objects
    if "brand_profile" in update_data and update_data["brand_profile"]:
        update_data["brand_profile"] = update_data["brand_profile"].model_dump() if hasattr(update_data["brand_profile"], 'model_dump') else update_data["brand_profile"]
    if "caption_rules" in update_data and update_data["caption_rules"]:
        update_data["caption_rules"] = update_data["caption_rules"].model_dump() if hasattr(update_data["caption_rules"], 'model_dump') else update_data["caption_rules"]

    for field, value in update_data.items():
        if value is not None:
            setattr(creator, field, value)

    db.commit()
    db.refresh(creator)
    return creator


@router.delete("/{creator_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_creator(
    creator_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a creator and all associated data."""
    creator = db.query(Creator).filter(Creator.id == creator_id).first()
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator not found"
        )

    db.delete(creator)
    db.commit()
    return None


@router.get("/{creator_id}/stats")
def get_creator_stats(
    creator_id: UUID,
    db: Session = Depends(get_db)
):
    """Get statistics for a creator."""
    from app.models.clip import Clip
    from app.models.generation import Generation

    creator = db.query(Creator).filter(Creator.id == creator_id).first()
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator not found"
        )

    clip_count = db.query(Clip).filter(Clip.creator_id == creator_id).count()
    generation_count = db.query(Generation).filter(Generation.creator_id == creator_id).count()
    completed_generations = db.query(Generation).filter(
        Generation.creator_id == creator_id,
        Generation.status == "completed"
    ).count()

    return {
        "creator_id": creator_id,
        "clip_count": clip_count,
        "generation_count": generation_count,
        "completed_generations": completed_generations,
    }
