"""
Audio track management API routes.
"""

import os
import shutil
from typing import Optional
from uuid import UUID
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_video_engine
from app.models.audio import AudioTrack
from app.schemas.audio import (
    AudioTrackCreate,
    AudioTrackUpdate,
    AudioTrackResponse,
    AudioTrackListResponse,
    BeatTimestamp,
)
from app.services.video_engine import VideoEngine
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.post("", response_model=AudioTrackResponse, status_code=status.HTTP_201_CREATED)
async def upload_audio(
    file: UploadFile = File(...),
    name: str = Form(...),
    context: str = Form("{}"),
    pacing_guide: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    video_engine: VideoEngine = Depends(get_video_engine)
):
    """Upload a new audio file."""
    import json

    # Validate file type
    allowed_types = ["audio/mpeg", "audio/mp3", "audio/wav", "audio/m4a", "audio/aac"]
    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {allowed_types}"
        )

    # Generate unique filename
    file_ext = Path(file.filename).suffix or ".mp3"
    unique_filename = f"{UUID(int=0).hex[:8]}_{file.filename}"
    file_path = Path(settings.audio_path) / unique_filename

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {e}"
        )

    # Get duration
    duration_ms = await video_engine.get_audio_duration_ms(str(file_path))

    # Parse context
    try:
        context_data = json.loads(context) if context else {}
    except json.JSONDecodeError:
        context_data = {}

    # Create database record
    audio_track = AudioTrack(
        name=name,
        file_path=str(file_path),
        duration_ms=duration_ms,
        context=context_data,
        beat_timestamps=[],
        pacing_guide=pacing_guide,
    )
    db.add(audio_track)
    db.commit()
    db.refresh(audio_track)

    return audio_track


@router.get("", response_model=AudioTrackListResponse)
def list_audio_tracks(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List all audio tracks with optional filtering."""
    query = db.query(AudioTrack)

    if search:
        query = query.filter(AudioTrack.name.ilike(f"%{search}%"))
    if is_active is not None:
        query = query.filter(AudioTrack.is_active == is_active)

    total = query.count()
    audio_tracks = query.offset(skip).limit(limit).all()

    return AudioTrackListResponse(audio_tracks=audio_tracks, total=total)


@router.get("/{audio_id}", response_model=AudioTrackResponse)
def get_audio_track(
    audio_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific audio track by ID."""
    audio = db.query(AudioTrack).filter(AudioTrack.id == audio_id).first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio track not found"
        )
    return audio


@router.put("/{audio_id}", response_model=AudioTrackResponse)
def update_audio_track(
    audio_id: UUID,
    audio_in: AudioTrackUpdate,
    db: Session = Depends(get_db)
):
    """Update an audio track."""
    audio = db.query(AudioTrack).filter(AudioTrack.id == audio_id).first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio track not found"
        )

    update_data = audio_in.model_dump(exclude_unset=True)

    # Handle nested objects
    if "context" in update_data and update_data["context"]:
        update_data["context"] = update_data["context"].model_dump() if hasattr(update_data["context"], 'model_dump') else update_data["context"]
    if "beat_timestamps" in update_data and update_data["beat_timestamps"]:
        update_data["beat_timestamps"] = [
            ts.model_dump() if hasattr(ts, 'model_dump') else ts
            for ts in update_data["beat_timestamps"]
        ]

    for field, value in update_data.items():
        if value is not None:
            setattr(audio, field, value)

    db.commit()
    db.refresh(audio)
    return audio


@router.put("/{audio_id}/timestamps", response_model=AudioTrackResponse)
def update_beat_timestamps(
    audio_id: UUID,
    timestamps: list[BeatTimestamp],
    db: Session = Depends(get_db)
):
    """Update beat timestamps for an audio track."""
    audio = db.query(AudioTrack).filter(AudioTrack.id == audio_id).first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio track not found"
        )

    audio.beat_timestamps = [ts.model_dump() for ts in timestamps]
    db.commit()
    db.refresh(audio)
    return audio


@router.delete("/{audio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_audio_track(
    audio_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an audio track and its file."""
    audio = db.query(AudioTrack).filter(AudioTrack.id == audio_id).first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio track not found"
        )

    # Delete file
    try:
        if os.path.exists(audio.file_path):
            os.remove(audio.file_path)
    except Exception as e:
        pass  # Log but don't fail on file deletion

    db.delete(audio)
    db.commit()
    return None


@router.get("/{audio_id}/waveform")
async def get_audio_waveform(
    audio_id: UUID,
    db: Session = Depends(get_db),
    video_engine: VideoEngine = Depends(get_video_engine)
):
    """Generate and return waveform image for an audio track."""
    from fastapi.responses import FileResponse

    audio = db.query(AudioTrack).filter(AudioTrack.id == audio_id).first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio track not found"
        )

    # Generate waveform
    waveform_path = Path(settings.temp_path) / f"waveform_{audio_id}.png"

    if not waveform_path.exists():
        await video_engine.extract_audio_waveform(
            audio.file_path,
            str(waveform_path)
        )

    return FileResponse(
        waveform_path,
        media_type="image/png",
        filename=f"waveform_{audio.name}.png"
    )
