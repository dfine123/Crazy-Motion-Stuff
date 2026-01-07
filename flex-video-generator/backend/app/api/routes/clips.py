"""
Clip management API routes.
"""

import os
import shutil
from typing import Optional
from uuid import UUID
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_twelve_labs_service, get_video_engine
from app.models.clip import Clip
from app.models.creator import Creator
from app.schemas.clip import (
    ClipCreate,
    ClipUpdate,
    ClipResponse,
    ClipListResponse,
    ClipUploadResponse,
)
from app.services.twelve_labs import TwelveLabsService
from app.services.video_engine import VideoEngine
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


async def analyze_clip_background(
    clip_id: UUID,
    file_path: str,
    creator_id: str,
    creator_name: str,
    db_url: str
):
    """Background task to analyze clip with Twelve Labs."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        twelve_labs = TwelveLabsService()
        index_id = await twelve_labs.get_or_create_creator_index(creator_id, creator_name)

        if index_id:
            result = await twelve_labs.upload_and_analyze_clip(file_path, index_id)

            clip = db.query(Clip).filter(Clip.id == clip_id).first()
            if clip and result.get("status") == "success":
                clip.analysis = result.get("analysis", {})
                clip.twelve_labs_video_id = result.get("twelve_labs_video_id")
                clip.twelve_labs_index_id = result.get("twelve_labs_index_id")
                db.commit()
    except Exception as e:
        import logging
        logging.error(f"Error analyzing clip {clip_id}: {e}")
    finally:
        db.close()


@router.post("/upload", response_model=ClipUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_clip(
    file: UploadFile = File(...),
    creator_id: UUID = Form(...),
    context: str = Form("{}"),
    analyze: bool = Form(True),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    video_engine: VideoEngine = Depends(get_video_engine)
):
    """Upload a new video clip with optional Twelve Labs analysis."""
    import json

    # Validate creator exists
    creator = db.query(Creator).filter(Creator.id == creator_id).first()
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator not found"
        )

    # Validate file type
    allowed_types = ["video/mp4", "video/quicktime", "video/x-msvideo", "video/webm"]
    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {allowed_types}"
        )

    # Create creator directory if needed
    creator_dir = Path(settings.clips_path) / str(creator_id)
    creator_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    import uuid as uuid_module
    unique_id = uuid_module.uuid4().hex[:8]
    file_ext = Path(file.filename).suffix or ".mp4"
    unique_filename = f"{unique_id}_{file.filename}"
    file_path = creator_dir / unique_filename

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {e}"
        )

    # Get video info
    video_info = video_engine._get_video_info(str(file_path))

    # Parse context
    try:
        context_data = json.loads(context) if context else {}
    except json.JSONDecodeError:
        context_data = {}

    # Create database record
    clip = Clip(
        creator_id=creator_id,
        file_path=str(file_path),
        duration_ms=video_info["duration_ms"],
        context=context_data,
        technical={
            "orientation": "vertical" if video_info["height"] > video_info["width"] else "horizontal",
            "resolution": f"{video_info['width']}x{video_info['height']}",
            "fps": video_info["fps"],
            "has_audio": False,
            "quality_score": 3
        },
        analysis={},
    )
    db.add(clip)
    db.commit()
    db.refresh(clip)

    # Generate thumbnail
    thumbnail_path = creator_dir / f"{unique_id}_thumb.jpg"
    try:
        await video_engine.generate_thumbnail(str(file_path), str(thumbnail_path))
        clip.thumbnail_path = str(thumbnail_path)
        db.commit()
    except Exception:
        pass  # Thumbnail generation is optional

    # Schedule background analysis if requested
    analysis_status = "pending" if analyze else "skipped"
    if analyze and background_tasks:
        background_tasks.add_task(
            analyze_clip_background,
            clip.id,
            str(file_path),
            str(creator_id),
            creator.name,
            settings.database_url
        )

    return ClipUploadResponse(
        clip_id=clip.id,
        file_path=str(file_path),
        analysis_status=analysis_status,
        analysis=None
    )


@router.post("/import")
async def import_clips_from_spreadsheet(
    file: UploadFile = File(...),
    creator_id: UUID = Form(...),
    analyze: bool = Form(False),
    db: Session = Depends(get_db)
):
    """Import clips from a CSV or Excel spreadsheet."""
    import pandas as pd
    import io

    # Validate creator exists
    creator = db.query(Creator).filter(Creator.id == creator_id).first()
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator not found"
        )

    # Read spreadsheet
    content = await file.read()
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read spreadsheet: {e}"
        )

    # Process each row
    results = []
    video_engine = VideoEngine()

    for _, row in df.iterrows():
        file_path = row.get("file_path")
        if not file_path or not os.path.exists(file_path):
            results.append({
                "file_path": file_path,
                "status": "error",
                "error": "File not found"
            })
            continue

        # Build context from spreadsheet columns
        context = {
            "flex_category": row.get("flex_category", "lifestyle"),
            "flex_intensity": int(row.get("flex_intensity", 3)),
            "mood": row.get("mood", "aspirational"),
            "best_for": str(row.get("best_for", "")).split(",") if row.get("best_for") else [],
            "location_type": row.get("location_type", ""),
            "custom_tags": str(row.get("custom_tags", "")).split(",") if row.get("custom_tags") else [],
        }

        # Get video info
        video_info = video_engine._get_video_info(file_path)

        # Create database record
        clip = Clip(
            creator_id=creator_id,
            file_path=file_path,
            duration_ms=video_info["duration_ms"],
            context=context,
            technical={
                "orientation": "vertical" if video_info["height"] > video_info["width"] else "horizontal",
                "resolution": f"{video_info['width']}x{video_info['height']}",
                "fps": video_info["fps"],
                "has_audio": False,
                "quality_score": 3
            },
            analysis={},
        )
        db.add(clip)
        results.append({
            "file_path": file_path,
            "status": "success"
        })

    db.commit()

    return {
        "imported": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "error"]),
        "results": results
    }


@router.get("", response_model=ClipListResponse)
def list_clips(
    creator_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    flex_category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List clips with optional filtering."""
    query = db.query(Clip)

    if creator_id:
        query = query.filter(Clip.creator_id == creator_id)
    if is_active is not None:
        query = query.filter(Clip.is_active == is_active)
    if flex_category:
        query = query.filter(Clip.context["flex_category"].astext == flex_category)

    total = query.count()
    clips = query.offset(skip).limit(limit).all()

    return ClipListResponse(clips=clips, total=total)


@router.get("/{clip_id}", response_model=ClipResponse)
def get_clip(
    clip_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific clip by ID."""
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clip not found"
        )
    return clip


@router.put("/{clip_id}", response_model=ClipResponse)
def update_clip(
    clip_id: UUID,
    clip_in: ClipUpdate,
    db: Session = Depends(get_db)
):
    """Update a clip's metadata."""
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clip not found"
        )

    update_data = clip_in.model_dump(exclude_unset=True)

    # Handle nested objects
    if "context" in update_data and update_data["context"]:
        update_data["context"] = update_data["context"].model_dump() if hasattr(update_data["context"], 'model_dump') else update_data["context"]
    if "technical" in update_data and update_data["technical"]:
        update_data["technical"] = update_data["technical"].model_dump() if hasattr(update_data["technical"], 'model_dump') else update_data["technical"]

    for field, value in update_data.items():
        if value is not None:
            setattr(clip, field, value)

    db.commit()
    db.refresh(clip)
    return clip


@router.delete("/{clip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_clip(
    clip_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a clip and its files."""
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clip not found"
        )

    # Delete files
    try:
        if os.path.exists(clip.file_path):
            os.remove(clip.file_path)
        if clip.thumbnail_path and os.path.exists(clip.thumbnail_path):
            os.remove(clip.thumbnail_path)
    except Exception:
        pass  # Log but don't fail on file deletion

    db.delete(clip)
    db.commit()
    return None


@router.post("/{clip_id}/reanalyze")
async def reanalyze_clip(
    clip_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger re-analysis of a clip with Twelve Labs."""
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clip not found"
        )

    creator = db.query(Creator).filter(Creator.id == clip.creator_id).first()

    background_tasks.add_task(
        analyze_clip_background,
        clip.id,
        clip.file_path,
        str(clip.creator_id),
        creator.name if creator else "Unknown",
        settings.database_url
    )

    return {"status": "analysis_queued", "clip_id": clip_id}
