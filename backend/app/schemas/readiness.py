from __future__ import annotations

from pydantic import BaseModel, Field


class ReadinessApiResponse(BaseModel):
    """Latest readiness from the same `run_readiness_agent` path as chat."""

    readiness_percent: int = Field(ge=0, le=100)
    readiness_signal: dict
    recommended_intensity: str = ""
    session_id: str | None = None
