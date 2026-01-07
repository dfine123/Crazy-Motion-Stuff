"""
Caption generation logic and optimization.
"""

import logging
from typing import Optional

from .claude_ai import ClaudeAIService

logger = logging.getLogger(__name__)


class CaptionGenerator:
    """Service for generating and optimizing Instagram captions."""

    def __init__(self):
        """Initialize caption generator."""
        self.claude_service = ClaudeAIService()

    async def generate_captions(
        self,
        creator_profile: dict,
        clip_descriptions: list[str],
        audio_mood: str,
        caption_rules: dict,
        count: int = 3
    ) -> list[dict]:
        """
        Generate multiple caption options for a video.

        Returns list of caption options with metadata.
        """
        result = await self.claude_service.generate_caption_only(
            creator_profile=creator_profile,
            clip_descriptions=clip_descriptions,
            audio_mood=audio_mood,
            caption_rules=caption_rules
        )

        if "error" in result:
            logger.error(f"Caption generation error: {result['error']}")
            return []

        return result.get("options", [])

    def validate_caption(
        self,
        caption: str,
        caption_rules: dict
    ) -> dict:
        """
        Validate a caption against rules.

        Returns validation result with any issues found.
        """
        issues = []
        warnings = []

        # Length checks
        max_length = caption_rules.get("max_length", 150)
        min_length = caption_rules.get("min_length", 50)

        if len(caption) > max_length:
            issues.append(f"Caption too long: {len(caption)} > {max_length}")
        if len(caption) < min_length:
            warnings.append(f"Caption might be too short: {len(caption)} < {min_length}")

        # Banned words check
        banned_words = caption_rules.get("banned_words", [])
        caption_lower = caption.lower()
        for word in banned_words:
            if word.lower() in caption_lower:
                issues.append(f"Contains banned word/phrase: '{word}'")

        # Emoji check
        emoji_usage = caption_rules.get("emoji_usage", "minimal")
        emoji_count = sum(1 for c in caption if ord(c) > 127462)  # Basic emoji detection

        if emoji_usage == "none" and emoji_count > 0:
            issues.append("Caption contains emojis but emoji_usage is 'none'")
        elif emoji_usage == "minimal" and emoji_count > 3:
            warnings.append(f"Caption has {emoji_count} emojis, but emoji_usage is 'minimal'")

        # Hashtag check
        hashtag_strategy = caption_rules.get("hashtag_strategy", "minimal")
        hashtag_count = caption.count("#")
        max_hashtags = caption_rules.get("hashtag_count", 3)

        if hashtag_strategy == "none" and hashtag_count > 0:
            issues.append("Caption contains hashtags but hashtag_strategy is 'none'")
        elif hashtag_count > max_hashtags:
            warnings.append(f"Caption has {hashtag_count} hashtags, max is {max_hashtags}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "stats": {
                "length": len(caption),
                "emoji_count": emoji_count,
                "hashtag_count": hashtag_count
            }
        }

    def format_caption(
        self,
        caption: str,
        formatting_rules: dict
    ) -> str:
        """
        Apply formatting rules to a caption.
        """
        line_breaks = formatting_rules.get("line_breaks", "strategic")
        capitalization = formatting_rules.get("capitalization", "normal")

        # Apply capitalization
        if capitalization == "all_lower":
            caption = caption.lower()
        elif capitalization == "strategic_caps":
            # Keep first letter of sentences capitalized, rest as-is
            pass

        # Apply line breaks
        if line_breaks == "none":
            caption = caption.replace("\n", " ")
        elif line_breaks == "every_sentence":
            # Add line break after each sentence
            for punct in [". ", "! ", "? "]:
                caption = caption.replace(punct, punct.strip() + "\n")

        return caption.strip()

    async def generate_with_selection(
        self,
        audio_context: dict,
        beat_timestamps: list[dict],
        creator_profile: dict,
        available_clips: list[dict],
        caption_rules: dict
    ) -> dict:
        """
        Generate both clip selection and caption in one call.

        This uses the full Claude AI service to select clips and generate
        a caption that matches the video content.
        """
        return await self.claude_service.select_clips_for_audio(
            audio_context=audio_context,
            beat_timestamps=beat_timestamps,
            creator_profile=creator_profile,
            available_clips=available_clips,
            caption_rules=caption_rules
        )
