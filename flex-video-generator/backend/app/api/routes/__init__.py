"""
API routes for the Flex Video Generator.
"""

from fastapi import APIRouter

from .creators import router as creators_router
from .audio import router as audio_router
from .clips import router as clips_router
from .generate import router as generate_router
from .settings import router as settings_router

api_router = APIRouter()

api_router.include_router(creators_router, prefix="/creators", tags=["creators"])
api_router.include_router(audio_router, prefix="/audio", tags=["audio"])
api_router.include_router(clips_router, prefix="/clips", tags=["clips"])
api_router.include_router(generate_router, prefix="/generate", tags=["generate"])
api_router.include_router(settings_router, prefix="/settings", tags=["settings"])
