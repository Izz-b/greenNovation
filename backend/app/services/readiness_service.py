"""Service layer for readiness/well-being check-ins."""

import uuid
from datetime import datetime
from collections import defaultdict
from typing import Optional

from backend.app.schemas.readiness import (
    CheckinRequest,
    CheckinResponse,
    ReadinessHistoryResponse,
    WeeklySummary,
)
from backend.app.schemas.forest import AwardTreeRequest


# In-memory storage (will be replaced with database in Phase 2)
_checkins: dict[str, list[dict]] = defaultdict(list)


async def submit_checkin(user_id: str, req: CheckinRequest) -> CheckinResponse:
    """
    Submit a daily well-being check-in.
    
    Awards a tree on first check-in of the day (daily login reward).
    
    Args:
        user_id: ID of the user submitting the check-in
        req: CheckinRequest with sleep, focus, mood, journal
    
    Returns:
        CheckinResponse with the stored check-in data
    """
    checkin_date = (req.date or datetime.utcnow()).strftime("%Y-%m-%d")
    
    # Check if user already checked in today
    today_checkin_exists = await get_today_checkin(user_id)
    
    checkin = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "date": checkin_date,
        "sleep": req.sleep,
        "focus": req.focus,
        "mood": req.mood,
        "journal": req.journal,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    # Store in memory
    _checkins[user_id].append(checkin)
    
    # Award tree on first daily check-in (daily login reward)
    if not today_checkin_exists:
        from backend.app.services.forest_service import ForestService
        dedupe_key = f"daily-checkin-{checkin_date}-{user_id}"
        award_req = AwardTreeRequest(
            reason="daily",
            message="Daily well-being check-in reward! Keep up the streak!",
            dedupe_key=dedupe_key,
        )
        ForestService.award_tree(user_id, award_req)
    
    return CheckinResponse(**checkin)


async def get_today_checkin(user_id: str) -> Optional[CheckinResponse]:
    """
    Get today's check-in if it exists.
    
    Args:
        user_id: ID of the user
    
    Returns:
        CheckinResponse if checked in today, None otherwise
    """
    today = datetime.utcnow().strftime("%Y-%m-%d")
    checkins = _checkins.get(user_id, [])
    
    for checkin in checkins:
        if checkin["date"] == today:
            return CheckinResponse(**checkin)
    
    return None


async def get_history(user_id: str, days: int = 7) -> ReadinessHistoryResponse:
    """
    Get historical check-ins and weekly summary.
    
    Args:
        user_id: ID of the user
        days: Number of days to retrieve (default 7)
    
    Returns:
        ReadinessHistoryResponse with checkins and week_summary
    """
    checkins = _checkins.get(user_id, [])
    
    # Get last N days
    recent = checkins[-days:] if len(checkins) > days else checkins
    
    # Compute weekly summary statistics
    mood_counts = defaultdict(int, {"happy": 0, "neutral": 0, "sad": 0})
    sleep_counts = defaultdict(int)
    focus_counts = defaultdict(int)
    
    for checkin in recent:
        mood_counts[checkin.get("mood", "neutral")] += 1
        sleep_counts[checkin.get("sleep", "okay")] += 1
        focus_counts[checkin.get("focus", "medium")] += 1
    
    total = len(recent) or 1
    
    # Determine average mood/sleep/focus
    def get_average(counts: dict) -> str:
        """Return the most common value."""
        if not counts:
            return "neutral"
        return max(counts, key=counts.get)
    
    week_summary = WeeklySummary(
        happy_pct=round(mood_counts["happy"] / total * 100),
        neutral_pct=round(mood_counts["neutral"] / total * 100),
        sad_pct=round(mood_counts["sad"] / total * 100),
        avg_sleep=get_average(sleep_counts),
        avg_focus=get_average(focus_counts),
        total_checkins=len(recent),
    )
    
    return ReadinessHistoryResponse(
        data=[CheckinResponse(**c) for c in recent],
        week_summary=week_summary,
    )
