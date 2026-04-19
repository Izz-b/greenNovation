"""API routes for well-being/readiness check-ins."""

from typing import Optional
from fastapi import APIRouter, Query

from backend.app.schemas.readiness import (
    CheckinRequest,
    CheckinResponse,
    ReadinessHistoryResponse,
)
from backend.app.services import readiness_service


router = APIRouter(tags=["readiness"], prefix="/api/readiness")


@router.post("/checkin", response_model=CheckinResponse)
async def submit_checkin(req: CheckinRequest) -> CheckinResponse:
    """
    Submit a daily well-being check-in.
    
    Submit your sleep quality, focus level, mood, and optional journal notes.
    
    **Request Body:**
    - `sleep`: "bad", "okay", or "great"
    - `focus`: "low", "medium", or "high"
    - `mood`: "sad", "neutral", or "happy"
    - `journal`: (optional) Free-text notes
    
    **Response:** CheckinResponse with auto-generated ID and timestamp
    """
    # TODO: Get user_id from JWT token when auth is implemented
    user_id = "default_user"
    
    return await readiness_service.submit_checkin(user_id, req)


@router.get("/current", response_model=Optional[CheckinResponse])
async def get_today() -> Optional[CheckinResponse]:
    """
    Get today's check-in if already submitted.
    
    Returns the check-in for today, or None if not checked in yet.
    Useful for pre-filling the form on page load.
    """
    # TODO: Get user_id from JWT token when auth is implemented
    user_id = "default_user"
    
    return await readiness_service.get_today_checkin(user_id)


@router.get("/history", response_model=ReadinessHistoryResponse)
async def get_history(days: int = Query(7, ge=1, le=90)) -> ReadinessHistoryResponse:
    """
    Get historical check-ins with weekly summary.
    
    **Query Parameters:**
    - `days`: Number of days to retrieve (1-90, default 7)
    
    **Response:** ReadinessHistoryResponse with checkin list and aggregated stats
    """
    # TODO: Get user_id from JWT token when auth is implemented
    user_id = "default_user"
    
    return await readiness_service.get_history(user_id, days)
