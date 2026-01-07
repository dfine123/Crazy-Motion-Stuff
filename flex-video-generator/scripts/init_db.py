#!/usr/bin/env python3
"""
Database initialization script for Flex Video Generator.

This script:
1. Creates all database tables
2. Creates a default caption optimization profile
3. Optionally creates sample data for testing
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os


def init_database(create_sample_data: bool = False):
    """Initialize the database with tables and optional sample data."""

    # Import after path setup
    from app.core.database import Base, engine
    from app.models import (
        Creator,
        AudioTrack,
        Clip,
        Generation,
        CaptionOptimizationProfile,
    )

    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

    # Create session
    Session = sessionmaker(bind=engine)
    db = Session()

    # Create default caption profile if it doesn't exist
    existing_profile = (
        db.query(CaptionOptimizationProfile)
        .filter(CaptionOptimizationProfile.is_default == True)
        .first()
    )

    if not existing_profile:
        print("Creating default caption optimization profile...")
        default_profile = CaptionOptimizationProfile(
            name="Default",
            is_default=True,
            rules={
                "hook_patterns": [
                    "Question that challenges viewer assumptions",
                    "Controversial but defensible statement",
                    "Specific number or result that creates curiosity",
                    "POV setup that creates immersion",
                    "This is what X looks like format",
                ],
                "structure": "hook → context → soft cta",
                "length_sweet_spot": {"min": 50, "max": 125, "ideal": 80},
                "formatting": {
                    "line_breaks": "strategic",
                    "capitalization": "normal",
                },
                "engagement_triggers": [
                    "create curiosity gap",
                    "imply exclusive knowledge",
                    "challenge common beliefs",
                    "promise transformation",
                ],
                "banned_patterns": [
                    "click link",
                    "dm me",
                    "comment below",
                    "follow for more",
                    "link in bio",
                ],
                "trending_formats": [
                    "This is what [X] looks like",
                    "POV: you finally [X]",
                    "The difference between [X] and [Y]",
                    "[Number] years of [X] taught me [Y]",
                ],
            },
        )
        db.add(default_profile)
        db.commit()
        print("Default caption profile created!")

    if create_sample_data:
        print("Creating sample data...")

        # Create sample creator
        sample_creator = Creator(
            name="Demo Creator",
            handle="democreator",
            brand_profile={
                "niche": "lifestyle",
                "tone": ["confident", "aspirational", "authentic"],
                "avoid": ["hype language", "clickbait", "desperate vibes"],
                "signature_phrases": [
                    "Build your vision",
                    "Freedom is a choice",
                ],
                "flex_style": "subtle",
                "lifestyle_themes": ["travel", "entrepreneurship", "freedom", "growth"],
            },
            caption_rules={
                "max_length": 150,
                "min_length": 50,
                "hashtag_strategy": "minimal",
                "hashtag_count": 3,
                "emoji_usage": "minimal",
                "cta_style": "soft",
                "voice": "first_person",
                "banned_words": ["link in bio", "dm me", "comment below"],
            },
        )
        db.add(sample_creator)
        db.commit()
        print(f"Sample creator created: {sample_creator.name} (ID: {sample_creator.id})")

    db.close()
    print("\nDatabase initialization complete!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize the Flex Video Generator database")
    parser.add_argument(
        "--sample-data",
        action="store_true",
        help="Create sample data for testing",
    )
    args = parser.parse_args()

    init_database(create_sample_data=args.sample_data)
