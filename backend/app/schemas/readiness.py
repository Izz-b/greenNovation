"""Pydantic models for well-being/readiness check-ins."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CheckinRequest(BaseModel):
    """Daily well-being check-in submission."""
    sleep: str = Field(..., description="Sleep quality: bad, okay, great")
    focus: str = Field(..., description="Focus level: low, medium, high")
    mood: str = Field(..., description="Mood: sad, neutral, happy")
    journal: Optional[str] = Field(None, description="Optional journal notes")
    date: Optional[datetime] = Field(None, description="Check-in date (defaults to today)")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "sleep": "great",
                "focus": "high",
                "mood": "happy",
                "journal": "Had a productive study session!"
            }]
        }
    }


class CheckinResponse(BaseModel):
    """Response after submitting a check-in."""
    id: str
    date: str
    sleep: str
    focus: str
    mood: str
    journal: Optional[str]
    created_at: str

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "date": "2026-04-19",
                "sleep": "great",
                "focus": "high",
                "mood": "happy",
                "journal": "Had a productive study session!",
                "created_at": "2026-04-19T14:30:00Z"
            }]
        }
    }


class WeeklySummary(BaseModel):
    """Weekly aggregated statistics."""
    happy_pct: int
    neutral_pct: int
    sad_pct: int
    avg_sleep: str
    avg_focus: str
    total_checkins: int


class ReadinessHistoryResponse(BaseModel):
    """Response for historical check-ins."""
    data: list[CheckinResponse]
    week_summary: WeeklySummary


class ReadinessApiResponse(BaseModel):
    """Latest readiness from the same `run_readiness_agent` path as chat."""

    readiness_percent: int = Field(ge=0, le=100)
    readiness_signal: dict
    recommended_intensity: str = ""
    session_id: str | None = None
