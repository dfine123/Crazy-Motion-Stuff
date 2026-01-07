#!/usr/bin/env python3
"""
Import clips from spreadsheet format.
Handles CSV and Excel files.
Optionally triggers Twelve Labs analysis for each clip.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import pandas as pd
import subprocess
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_video_info(file_path: str) -> dict:
    """Get video metadata using ffprobe."""
    try:
        # Get duration
        duration_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ]
        result = subprocess.run(duration_cmd, capture_output=True, text=True, check=True)
        duration_ms = int(float(result.stdout.strip()) * 1000)

        # Get video info
        info_cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate",
            "-of", "csv=p=0",
            file_path
        ]
        result = subprocess.run(info_cmd, capture_output=True, text=True, check=True)
        parts = result.stdout.strip().split(",")

        width = int(parts[0]) if len(parts) > 0 else 1080
        height = int(parts[1]) if len(parts) > 1 else 1920

        fps_str = parts[2] if len(parts) > 2 else "30/1"
        if "/" in fps_str:
            num, den = fps_str.split("/")
            fps = int(num) / int(den) if int(den) != 0 else 30
        else:
            fps = float(fps_str)

        return {
            "duration_ms": duration_ms,
            "width": width,
            "height": height,
            "fps": round(fps),
            "orientation": "vertical" if height > width else "horizontal",
        }
    except Exception as e:
        print(f"Warning: Could not get video info for {file_path}: {e}")
        return {
            "duration_ms": 0,
            "width": 1080,
            "height": 1920,
            "fps": 30,
            "orientation": "vertical",
        }


async def import_clips(
    spreadsheet_path: str,
    creator_id: str,
    analyze_with_twelve_labs: bool = False
):
    """Import clips from a CSV or Excel spreadsheet."""

    from app.core.database import engine
    from app.models.clip import Clip
    from app.models.creator import Creator

    # Load spreadsheet
    if spreadsheet_path.endswith(".csv"):
        df = pd.read_csv(spreadsheet_path)
    else:
        df = pd.read_excel(spreadsheet_path)

    print(f"Found {len(df)} rows in spreadsheet")

    # Create session
    Session = sessionmaker(bind=engine)
    db = Session()

    # Verify creator exists
    creator = db.query(Creator).filter(Creator.id == creator_id).first()
    if not creator:
        print(f"Error: Creator with ID {creator_id} not found")
        db.close()
        return

    print(f"Importing clips for creator: {creator.name}")

    # Initialize Twelve Labs if needed
    twelve_labs = None
    index_id = None
    if analyze_with_twelve_labs:
        try:
            from app.services.twelve_labs import TwelveLabsService
            twelve_labs = TwelveLabsService()
            index_id = await twelve_labs.get_or_create_creator_index(
                str(creator_id), creator.name
            )
            if index_id:
                print(f"Using Twelve Labs index: {index_id}")
            else:
                print("Warning: Could not create Twelve Labs index, skipping analysis")
                twelve_labs = None
        except Exception as e:
            print(f"Warning: Twelve Labs not available: {e}")
            twelve_labs = None

    results = {"success": 0, "failed": 0, "errors": []}

    for idx, row in df.iterrows():
        file_path = row.get("file_path")

        if not file_path:
            results["failed"] += 1
            results["errors"].append(f"Row {idx}: Missing file_path")
            continue

        if not os.path.exists(file_path):
            results["failed"] += 1
            results["errors"].append(f"Row {idx}: File not found: {file_path}")
            continue

        print(f"Processing: {file_path}")

        # Get video info
        video_info = get_video_info(file_path)

        # Build context from spreadsheet columns
        context = {
            "flex_category": str(row.get("flex_category", "lifestyle")),
            "flex_intensity": int(row.get("flex_intensity", 3)),
            "mood": str(row.get("mood", "aspirational")),
            "best_for": [s.strip() for s in str(row.get("best_for", "")).split(",") if s.strip()],
            "avoid_pairing_with": [],
            "season": "any",
            "location_type": str(row.get("location_type", "")),
            "custom_tags": [s.strip() for s in str(row.get("custom_tags", "")).split(",") if s.strip()],
        }

        technical = {
            "orientation": video_info["orientation"],
            "resolution": f"{video_info['width']}x{video_info['height']}",
            "fps": video_info["fps"],
            "has_audio": False,
            "quality_score": 3,
        }

        analysis = {}

        # Analyze with Twelve Labs if available
        if twelve_labs and index_id:
            try:
                result = await twelve_labs.upload_and_analyze_clip(file_path, index_id)
                if result.get("status") == "success":
                    analysis = result.get("analysis", {})
                    print(f"  Twelve Labs analysis complete")
            except Exception as e:
                print(f"  Warning: Twelve Labs analysis failed: {e}")

        # Create clip record
        clip = Clip(
            creator_id=creator_id,
            file_path=file_path,
            duration_ms=video_info["duration_ms"],
            context=context,
            technical=technical,
            analysis=analysis,
        )

        db.add(clip)
        results["success"] += 1
        print(f"  Added clip: {clip.id}")

    db.commit()
    db.close()

    print("\n" + "=" * 50)
    print("Import Complete!")
    print(f"  Success: {results['success']}")
    print(f"  Failed: {results['failed']}")

    if results["errors"]:
        print("\nErrors:")
        for error in results["errors"]:
            print(f"  - {error}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Import clips from a CSV or Excel spreadsheet"
    )
    parser.add_argument("spreadsheet", help="Path to CSV or Excel file")
    parser.add_argument("--creator-id", required=True, help="Creator UUID")
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze clips with Twelve Labs (requires API key)",
    )
    args = parser.parse_args()

    asyncio.run(
        import_clips(
            args.spreadsheet,
            args.creator_id,
            analyze_with_twelve_labs=args.analyze,
        )
    )
