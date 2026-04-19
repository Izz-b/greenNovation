from __future__ import annotations

from fastapi import APIRouter, Query

from backend.app.schemas.readiness import ReadinessApiResponse
from backend.app.services.readiness_dashboard_service import compute_dashboard_readiness

router = APIRouter(tags=["readiness"])


@router.get("/api/readiness", response_model=ReadinessApiResponse)
def get_readiness(
    session_id: str | None = Query(
        default=None,
        description="Optional chat session id: merges stored passive_behavior_signals from that session.",
    ),
):
    data = compute_dashboard_readiness(session_id)
    return ReadinessApiResponse(**data)
