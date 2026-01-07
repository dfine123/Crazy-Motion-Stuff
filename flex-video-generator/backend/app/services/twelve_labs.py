"""
Twelve Labs integration for automatic clip analysis.

Uses Pegasus 1.2 model for video understanding and description generation.
Creates a dedicated index per creator for organized storage.
"""

import json
import logging
from typing import Optional, Callable
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TwelveLabsService:
    """Service for interacting with Twelve Labs API."""

    def __init__(self):
        """Initialize Twelve Labs client."""
        self.api_key = settings.twelve_labs_api_key
        self._client = None

    @property
    def client(self):
        """Lazy load the Twelve Labs client."""
        if self._client is None:
            if not self.api_key:
                logger.warning("Twelve Labs API key not configured")
                return None
            try:
                from twelvelabs import TwelveLabs
                self._client = TwelveLabs(api_key=self.api_key)
            except ImportError:
                logger.error("twelvelabs package not installed")
                return None
        return self._client

    async def get_or_create_creator_index(self, creator_id: str, creator_name: str) -> Optional[str]:
        """
        Get existing index for creator or create new one.
        Index naming: flex-{creator_id[:8]}
        """
        if not self.client:
            return None

        index_name = f"flex-{creator_id[:8]}"

        try:
            # Check if index exists
            indexes = self.client.index.list()
            for idx in indexes:
                if idx.name == index_name:
                    return idx.id

            # Create new index with Pegasus model for analysis
            index = self.client.index.create(
                name=index_name,
                models=[
                    {
                        "name": "pegasus1.2",
                        "options": ["visual", "audio"]
                    },
                    {
                        "name": "marengo2.6",
                        "options": ["visual", "audio"]
                    }
                ]
            )
            return index.id
        except Exception as e:
            logger.error(f"Error creating/getting index: {e}")
            return None

    async def upload_and_analyze_clip(
        self,
        file_path: str,
        index_id: str,
        custom_prompt: Optional[str] = None
    ) -> dict:
        """
        Upload clip to Twelve Labs and get comprehensive analysis.

        Returns structured metadata for storage in clips table.
        """
        if not self.client:
            return {
                "status": "error",
                "error": "Twelve Labs client not configured"
            }

        try:
            # Upload and index the video
            task = self.client.task.create(
                index_id=index_id,
                file=file_path,
                language="en"
            )

            # Wait for indexing to complete
            task.wait_for_done(sleep_interval=5)
            video_id = task.video_id

            # Generate comprehensive analysis using custom prompt
            analysis_prompt = custom_prompt or """
            Analyze this video clip for use in Instagram flex/lifestyle content.

            Provide a detailed JSON response with:
            1. visual_content: Detailed description of what's shown (2-3 sentences)
            2. detected_objects: Array of luxury/lifestyle items visible
            3. detected_actions: What's happening in the clip
            4. scene_type: indoor/outdoor/aerial/pov/wide
            5. mood: The emotional tone (aspirational/exclusive/casual/energetic/peaceful)
            6. flex_category: Main category (travel/cars/watches/lifestyle/money/property/experiences)
            7. flex_intensity: 1-5 scale of how "flex" this content is
            8. best_for: Array of video sections this works for (reveals/drops/intros/sustains/finales)
            9. location_type: Specific location category if identifiable
            10. has_faces: Boolean
            11. quality_assessment: Brief note on video quality

            Return ONLY valid JSON, no additional text.
            """

            analysis_response = self.client.generate.text(
                video_id=video_id,
                prompt=analysis_prompt
            )

            # Also get gist for additional context
            gist = self.client.generate.gist(
                video_id=video_id,
                types=["title", "topic", "hashtag"]
            )

            # Parse and structure the response
            try:
                analysis_data = json.loads(analysis_response.data)
            except (json.JSONDecodeError, AttributeError):
                # Fallback if JSON parsing fails
                analysis_data = {
                    "visual_content": str(analysis_response.data) if hasattr(analysis_response, 'data') else str(analysis_response),
                    "detected_objects": [],
                    "parse_error": True
                }

            return {
                "twelve_labs_video_id": video_id,
                "twelve_labs_index_id": index_id,
                "analysis": analysis_data,
                "gist": {
                    "title": getattr(gist, 'title', ''),
                    "topics": getattr(gist, 'topics', []),
                    "hashtags": getattr(gist, 'hashtags', [])
                },
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Error analyzing clip: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def batch_upload_clips(
        self,
        file_paths: list[str],
        creator_id: str,
        creator_name: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> list[dict]:
        """
        Upload multiple clips with progress tracking.
        """
        index_id = await self.get_or_create_creator_index(creator_id, creator_name)

        if not index_id:
            return [{
                "file_path": fp,
                "status": "error",
                "error": "Could not create/get index"
            } for fp in file_paths]

        results = []

        for i, file_path in enumerate(file_paths):
            try:
                result = await self.upload_and_analyze_clip(file_path, index_id)
                result["file_path"] = file_path
                results.append(result)
            except Exception as e:
                results.append({
                    "file_path": file_path,
                    "status": "error",
                    "error": str(e)
                })

            if progress_callback:
                progress_callback(i + 1, len(file_paths))

        return results

    async def search_similar_clips(
        self,
        index_id: str,
        query: str,
        limit: int = 10
    ) -> list[dict]:
        """
        Search for clips matching a description.
        """
        if not self.client:
            return []

        try:
            search_results = self.client.search.query(
                index_id=index_id,
                query_text=query,
                options=["visual", "audio"],
                limit=limit
            )

            return [
                {
                    "video_id": result.video_id,
                    "score": result.score,
                    "start": result.start,
                    "end": result.end
                }
                for result in search_results.data
            ]
        except Exception as e:
            logger.error(f"Error searching clips: {e}")
            return []
