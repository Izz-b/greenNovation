from __future__ import annotations

from datetime import date
from typing import Any

from ai.agents.readiness.agent import run_readiness_agent

from backend.app.schemas.project import Project
from backend.app.services import projects_service
from backend.app.services import session_service as sessions


def _project_progress_fraction(p: Project) -> float:
    m = p.milestones
    if not m:
        return 0.0
    return sum(1 for x in m if x.done) / len(m)


def passive_behavior_signals_from_projects(projects: list[Project]) -> dict[str, Any]:
    """Derive ReadinessInput-shaped passive signals from saved projects (deadlines + milestones)."""
    if not projects:
        return dict(sessions.default_session_state()["passive_behavior_signals"])

    today = date.today()
    overdue = 0
    due_3d = 0
    completion_fracs: list[float] = []

    for p in projects:
        try:
            due = date.fromisoformat(p.dueISO)
        except ValueError:
            continue
        days = (due - today).days
        if days < 0:
            overdue += 1
        if 0 <= days <= 3:
            due_3d += 1
        completion_fracs.append(_project_progress_fraction(p))

    risk: str = "low"
    if overdue >= 2 or due_3d >= 4:
        risk = "high"
    elif overdue >= 1 or due_3d >= 2:
        risk = "medium"

    avg_completion = (
        sum(completion_fracs) / len(completion_fracs) if completion_fracs else 0.8
    )

    return {
        "tasks_due_3d": min(due_3d, 5),
        "overdue_tasks": min(overdue, 5),
        "project_risk_level": risk,
        "study_sessions_last_7d": 5,
        "avg_session_completion_rate": round(min(1.0, max(0.0, avg_completion)), 2),
        "avg_quiz_score_trend": 0.0,
        "late_night_activity_ratio": 0.1,
        "long_sessions_without_breaks": 0,
    }


def _merge_passive(base: dict[str, Any], overlay: dict[str, Any] | None) -> dict[str, Any]:
    out = {**base}
    if overlay:
        out.update(overlay)
    return out


def readiness_percent_from_signal(sig: dict[str, Any]) -> int:
    """Single 0–100 score: high when workload/performance/fatigue risks are low and stability is high."""
    w = float(sig.get("workload_pressure_score", 0.0))
    s = float(sig.get("study_stability_score", 0.0))
    p = float(sig.get("performance_trend_score", 0.0))
    f = float(sig.get("behavioral_fatigue_score", 0.0))
    raw = ((1.0 - w) + s + (1.0 - p) + (1.0 - f)) / 4.0
    return max(0, min(100, round(raw * 100)))


def compute_dashboard_readiness(session_id: str | None) -> dict[str, Any]:
    projects = projects_service.load_projects()
    from_projects = passive_behavior_signals_from_projects(projects)

    session_overlay: dict[str, Any] | None = None
    if session_id:
        sess = sessions.load_session_copy(session_id)
        if sess:
            session_overlay = sess.get("passive_behavior_signals") or None

    passive = _merge_passive(from_projects, session_overlay)
    state: dict[str, Any] = {"passive_behavior_signals": passive}
    run_readiness_agent(state)
    sig = state.get("readiness_signal") or {}
    pct = readiness_percent_from_signal(sig)
    intensity = str(sig.get("recommended_intensity") or "")
    return {
        "readiness_percent": pct,
        "readiness_signal": sig,
        "recommended_intensity": intensity,
        "session_id": session_id,
    }
