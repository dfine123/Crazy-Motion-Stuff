"""
Claude API integration for intelligent clip selection and caption generation.
"""

import json
import logging
from typing import Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ClaudeAIService:
    """Service for interacting with Anthropic Claude API."""

    def __init__(self):
        """Initialize Claude client."""
        self.api_key = settings.anthropic_api_key
        self.model = settings.claude_model
        self._client = None

    @property
    def client(self):
        """Lazy load the Anthropic client."""
        if self._client is None:
            if not self.api_key:
                logger.warning("Anthropic API key not configured")
                return None
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                logger.error("anthropic package not installed")
                return None
        return self._client

    async def select_clips_for_audio(
        self,
        audio_context: dict,
        beat_timestamps: list[dict],
        creator_profile: dict,
        available_clips: list[dict],
        caption_rules: dict
    ) -> dict:
        """
        Use Claude to intelligently select and order clips based on:
        - Audio beat structure and mood
        - Creator brand voice and style
        - Clip content and flex intensity
        - Caption optimization rules

        Returns: {clip_sequence: [], caption: str, reasoning: str}
        """
        if not self.client:
            return {
                "error": "Claude client not configured",
                "clip_sequence": [],
                "caption": "",
                "overall_reasoning": ""
            }

        prompt = f"""You are an expert Instagram content strategist specializing in "flex" and lifestyle content. Your task is to select and order video clips to create a compelling Instagram reel.

## AUDIO CONTEXT
{json.dumps(audio_context, indent=2)}

## BEAT TIMESTAMPS (clips must sync to these)
{json.dumps(beat_timestamps, indent=2)}

## CREATOR BRAND PROFILE
{json.dumps(creator_profile, indent=2)}

## AVAILABLE CLIPS
Each clip has: id, duration_ms, visual_content, flex_category, flex_intensity, mood, best_for, location_type
{json.dumps(available_clips, indent=2)}

## CAPTION OPTIMIZATION RULES
{json.dumps(caption_rules, indent=2)}

## YOUR TASK

1. **Select clips** that:
   - Match the creator's brand voice and lifestyle themes
   - Build visual narrative that complements the audio energy
   - Hit beat timestamps with appropriate intensity clips
   - Create variety while maintaining cohesion

2. **Order clips** so that:
   - Intro beats get establishing/lifestyle shots
   - Build sections create anticipation
   - Drop moments feature highest-intensity flex content
   - Sustain sections maintain energy
   - Transitions feel natural

3. **Generate caption** that:
   - Follows all caption rules exactly
   - Uses a hook pattern from the rules
   - Matches creator's voice and tone
   - Creates curiosity without being clickbait
   - Stays within length limits

## RESPONSE FORMAT (JSON only)

Return ONLY this JSON structure, no other text:

{{
    "clip_sequence": [
        {{
            "clip_id": "uuid",
            "beat_segment": "intro|build|drop|sustain|outro",
            "start_ms": 0,
            "end_ms": 3500,
            "reasoning": "Why this clip for this moment"
        }}
    ],
    "caption": "The generated caption text",
    "caption_analysis": {{
        "hook_type_used": "which hook pattern",
        "estimated_length": 85,
        "cta_included": true
    }},
    "overall_reasoning": "Brief explanation of selection strategy"
}}
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract and parse JSON from response
            response_text = response.content[0].text

            # Handle potential markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            return json.loads(response_text.strip())

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response: {e}")
            return {
                "error": f"Failed to parse response: {e}",
                "clip_sequence": [],
                "caption": "",
                "overall_reasoning": ""
            }
        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            return {
                "error": str(e),
                "clip_sequence": [],
                "caption": "",
                "overall_reasoning": ""
            }

    async def generate_caption_only(
        self,
        creator_profile: dict,
        clip_descriptions: list[str],
        audio_mood: str,
        caption_rules: dict
    ) -> dict:
        """
        Generate just a caption based on selected clips and context.
        Useful for regenerating captions without re-selecting clips.
        """
        if not self.client:
            return {
                "error": "Claude client not configured",
                "options": []
            }

        prompt = f"""Generate an Instagram caption for a flex/lifestyle reel.

CREATOR VOICE: {json.dumps(creator_profile, indent=2)}

CLIPS IN VIDEO (in order):
{chr(10).join(f"- {desc}" for desc in clip_descriptions)}

AUDIO MOOD: {audio_mood}

CAPTION RULES:
{json.dumps(caption_rules, indent=2)}

Generate 3 caption options, each following different hook patterns from the rules.

Return JSON only:
{{
    "options": [
        {{"caption": "...", "hook_type": "...", "length": 85}},
        {{"caption": "...", "hook_type": "...", "length": 92}},
        {{"caption": "...", "hook_type": "...", "length": 78}}
    ]
}}
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = response.content[0].text
            if "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            return json.loads(response_text.strip())

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response: {e}")
            return {
                "error": f"Failed to parse response: {e}",
                "options": []
            }
        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            return {
                "error": str(e),
                "options": []
            }

    async def enhance_clip_metadata(
        self,
        clip_analysis: dict,
        creator_profile: dict
    ) -> dict:
        """
        Use Claude to enhance clip metadata based on Twelve Labs analysis
        and creator context.
        """
        if not self.client:
            return clip_analysis

        prompt = f"""Given this video clip analysis from Twelve Labs and the creator's brand profile,
enhance the metadata with additional context useful for Instagram flex content.

CLIP ANALYSIS:
{json.dumps(clip_analysis, indent=2)}

CREATOR PROFILE:
{json.dumps(creator_profile, indent=2)}

Return enhanced metadata JSON with:
- flex_category: travel|cars|watches|lifestyle|money|property|experiences
- flex_intensity: 1-5 scale
- mood: aspirational|exclusive|casual|energetic|peaceful
- best_for: array of video sections (reveals|drops|intros|sustains|finales)
- suggested_captions: 2-3 short caption ideas specific to this clip
- brand_alignment_score: 1-5 how well this fits the creator's brand

Return JSON only.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = response.content[0].text
            if "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            enhanced = json.loads(response_text.strip())
            # Merge with original analysis
            return {**clip_analysis, **enhanced}

        except Exception as e:
            logger.error(f"Error enhancing clip metadata: {e}")
            return clip_analysis
