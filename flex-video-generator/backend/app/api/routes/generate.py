"""
Video generation API routes.
"""

import os
from typing import Optional
from uuid import UUID
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_claude_service, get_video_engine, get_caption_generator
from app.models.generation import Generation
from app.models.creator import Creator
from app.models.audio import AudioTrack
from app.models.clip import Clip
from app.schemas.generation import (
    GenerationCreate,
    GenerationResponse,
    GenerationListResponse,
    GenerationStatus,
    RegenerateCaptionRequest,
    RegenerateCaptionResponse,
)
from app.services.claude_ai import ClaudeAIService
from app.services.video_engine import VideoEngine
from app.services.caption_gen import CaptionGenerator
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


async def process_generation_background(
    generation_id: UUID,
    db_url: str
):
    """Background task to process video generation."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import logging

    logger = logging.getLogger(__name__)

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        generation = db.query(Generation).filter(Generation.id == generation_id).first()
        if not generation:
            return

        generation.status = "processing"
        db.commit()

        # Get related data
        creator = db.query(Creator).filter(Creator.id == generation.creator_id).first()
        audio = db.query(AudioTrack).filter(AudioTrack.id == generation.audio_id).first()

        if not creator or not audio:
            generation.status = "failed"
            generation.error_message = "Creator or audio not found"
            db.commit()
            return

        # Get available clips for this creator
        clips = db.query(Clip).filter(
            Clip.creator_id == generation.creator_id,
            Clip.is_active == True
        ).all()

        if not clips:
            generation.status = "failed"
            generation.error_message = "No clips available for this creator"
            db.commit()
            return

        # Prepare clip data for AI
        available_clips = [
            {
                "id": str(clip.id),
                "duration_ms": clip.duration_ms,
                "visual_content": clip.analysis.get("visual_content", ""),
                "flex_category": clip.context.get("flex_category", "lifestyle"),
                "flex_intensity": clip.context.get("flex_intensity", 3),
                "mood": clip.context.get("mood", "aspirational"),
                "best_for": clip.context.get("best_for", []),
                "location_type": clip.context.get("location_type", ""),
            }
            for clip in clips
        ]

        # Use Claude to select clips and generate caption
        claude_service = ClaudeAIService()
        result = await claude_service.select_clips_for_audio(
            audio_context=audio.context,
            beat_timestamps=audio.beat_timestamps,
            creator_profile=creator.brand_profile,
            available_clips=available_clips,
            caption_rules=creator.caption_rules
        )

        if "error" in result:
            generation.status = "failed"
            generation.error_message = result["error"]
            db.commit()
            return

        # Update generation with AI results
        generation.clip_sequence = result.get("clip_sequence", [])
        generation.caption = result.get("caption", "")
        generation.caption_metadata = result.get("caption_analysis", {})
        generation.ai_reasoning = {"overall_reasoning": result.get("overall_reasoning", "")}
        db.commit()

        # Build clip sequence with file paths
        clip_lookup = {str(clip.id): clip for clip in clips}
        render_sequence = []

        for seq_item in generation.clip_sequence:
            clip_id = seq_item.get("clip_id")
            clip = clip_lookup.get(clip_id)
            if clip:
                render_sequence.append({
                    "clip_path": clip.file_path,
                    "clip_start_ms": 0,
                    "start_ms": seq_item.get("start_ms", 0),
                    "end_ms": seq_item.get("end_ms", clip.duration_ms),
                    "beat_segment": seq_item.get("beat_segment", "sustain")
                })

        if not render_sequence:
            generation.status = "failed"
            generation.error_message = "No valid clips in sequence"
            db.commit()
            return

        # Render video
        video_engine = VideoEngine()

        # Create output directory
        output_dir = Path(settings.exports_path) / str(generation.creator_id)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_filename = f"gen_{generation.id.hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        output_path = output_dir / output_filename

        try:
            await video_engine.render_video(
                clip_sequence=render_sequence,
                audio_path=audio.file_path,
                caption="",  # Caption overlay disabled for now
                output_path=str(output_path)
            )

            generation.output_path = str(output_path)
            generation.status = "completed"
            generation.completed_at = datetime.utcnow()
        except Exception as e:
            generation.status = "failed"
            generation.error_message = f"Rendering failed: {str(e)}"
            logger.error(f"Rendering failed for generation {generation_id}: {e}")

        db.commit()

    except Exception as e:
        logger.error(f"Error processing generation {generation_id}: {e}")
        try:
            generation = db.query(Generation).filter(Generation.id == generation_id).first()
            if generation:
                generation.status = "failed"
                generation.error_message = str(e)
                db.commit()
        except:
            pass
    finally:
        db.close()


@router.post("", response_model=GenerationResponse, status_code=status.HTTP_201_CREATED)
async def create_generation(
    generation_in: GenerationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start a new video generation job."""
    # Validate creator exists
    creator = db.query(Creator).filter(Creator.id == generation_in.creator_id).first()
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator not found"
        )

    # Validate audio exists
    audio = db.query(AudioTrack).filter(AudioTrack.id == generation_in.audio_id).first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio track not found"
        )

    # Create generation record
    generation = Generation(
        creator_id=generation_in.creator_id,
        audio_id=generation_in.audio_id,
        status="pending",
        clip_sequence=[],
    )
    db.add(generation)
    db.commit()
    db.refresh(generation)

    # Start background processing
    background_tasks.add_task(
        process_generation_background,
        generation.id,
        settings.database_url
    )

    return generation


@router.get("", response_model=GenerationListResponse)
def list_generations(
    creator_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List generation jobs with optional filtering."""
    query = db.query(Generation)

    if creator_id:
        query = query.filter(Generation.creator_id == creator_id)
    if status:
        query = query.filter(Generation.status == status)

    query = query.order_by(Generation.created_at.desc())

    total = query.count()
    generations = query.offset(skip).limit(limit).all()

    return GenerationListResponse(generations=generations, total=total)


@router.get("/history")
def get_generation_history(
    creator_id: Optional[UUID] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get recent generation history."""
    query = db.query(Generation).filter(Generation.status == "completed")

    if creator_id:
        query = query.filter(Generation.creator_id == creator_id)

    generations = query.order_by(Generation.completed_at.desc()).limit(limit).all()

    return {
        "generations": [
            {
                "id": gen.id,
                "creator_id": gen.creator_id,
                "audio_id": gen.audio_id,
                "caption": gen.caption,
                "output_path": gen.output_path,
                "completed_at": gen.completed_at,
            }
            for gen in generations
        ]
    }


@router.get("/{generation_id}", response_model=GenerationResponse)
def get_generation(
    generation_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific generation by ID."""
    generation = db.query(Generation).filter(Generation.id == generation_id).first()
    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found"
        )
    return generation


@router.post("/{generation_id}/regenerate-caption", response_model=RegenerateCaptionResponse)
async def regenerate_caption(
    generation_id: UUID,
    request: RegenerateCaptionRequest,
    db: Session = Depends(get_db),
    caption_generator: CaptionGenerator = Depends(get_caption_generator)
):
    """Regenerate caption for an existing generation, keeping clips."""
    generation = db.query(Generation).filter(Generation.id == generation_id).first()
    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found"
        )

    creator = db.query(Creator).filter(Creator.id == generation.creator_id).first()
    audio = db.query(AudioTrack).filter(AudioTrack.id == generation.audio_id).first()

    if not creator or not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator or audio not found"
        )

    # Get clip descriptions from sequence
    clip_descriptions = []
    for seq_item in generation.clip_sequence:
        clip = db.query(Clip).filter(Clip.id == seq_item.get("clip_id")).first()
        if clip:
            desc = clip.analysis.get("visual_content", "") or clip.context.get("flex_category", "clip")
            clip_descriptions.append(desc)

    # Generate new captions
    captions = await caption_generator.generate_captions(
        creator_profile=creator.brand_profile,
        clip_descriptions=clip_descriptions,
        audio_mood=audio.context.get("mood", "energetic"),
        caption_rules=creator.caption_rules
    )

    return RegenerateCaptionResponse(
        caption_options=captions,
        selected_caption=None
    )


@router.put("/{generation_id}/caption")
def update_generation_caption(
    generation_id: UUID,
    caption: str,
    db: Session = Depends(get_db)
):
    """Update the caption for a generation."""
    generation = db.query(Generation).filter(Generation.id == generation_id).first()
    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found"
        )

    generation.caption = caption
    db.commit()
    db.refresh(generation)

    return {"status": "updated", "caption": generation.caption}


@router.delete("/{generation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_generation(
    generation_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a generation and its output file."""
    generation = db.query(Generation).filter(Generation.id == generation_id).first()
    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found"
        )

    # Delete output file
    try:
        if generation.output_path and os.path.exists(generation.output_path):
            os.remove(generation.output_path)
    except Exception:
        pass

    db.delete(generation)
    db.commit()
    return None
