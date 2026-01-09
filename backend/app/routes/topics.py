"""Topics endpoint for conversation scenarios."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/topics", tags=["topics"])

# Load topics data from static file
_TOPICS_FILE = Path(__file__).resolve().parent.parent / "static" / "topics.json"


@router.get("")
async def get_topics():
    """Get all conversation topics with starters.

    Returns a list of topics with names, descriptions, and conversation starters
    in all supported languages (Spanish, Italian, German, French, Dutch).
    """
    try:
        with open(_TOPICS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Topics data file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid topics data format")
