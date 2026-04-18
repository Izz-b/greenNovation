from __future__ import annotations

from .schemas import ReadinessInput


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def normalize_count(value: int, max_value: int) -> float:
    if max_value <= 0:
        return 0.0
    return clamp01(value / max_value)


def risk_level_to_score(risk: str) -> float:
    mapping = {
        "low": 0.2,
        "medium": 0.6,
        "high": 1.0,
    }
    return mapping.get(risk, 0.2)


def negative_trend_to_risk(value: float, max_drop: float = 20.0) -> float:
    """
    Converts a negative trend into a risk score.
    0 or positive trend -> 0.0 risk
    -max_drop or lower -> 1.0 risk
    """
    if value >= 0:
        return 0.0
    return clamp01(abs(value) / max_drop)


def compute_workload_pressure_score(data: ReadinessInput) -> float:
    score = (
        normalize_count(data.tasks_due_3d, 5) * 0.40
        + normalize_count(data.overdue_tasks, 5) * 0.30
        + risk_level_to_score(data.project_risk_level) * 0.30
    )
    return round(clamp01(score), 4)


def compute_study_stability_score(data: ReadinessInput) -> float:
    """
    Higher = more stable
    """
    score = (
        normalize_count(data.study_sessions_last_7d, 7) * 0.45
        + clamp01(data.avg_session_completion_rate) * 0.55
    )
    return round(clamp01(score), 4)


def compute_performance_trend_score(data: ReadinessInput) -> float:
    """
    Higher = worse performance trend
    """
    score = negative_trend_to_risk(data.avg_quiz_score_trend, max_drop=20.0)
    return round(clamp01(score), 4)


def compute_behavioral_fatigue_score(data: ReadinessInput) -> float:
    """
    Higher = more fatigue-related behavior
    """
    score = (
        clamp01(data.late_night_activity_ratio) * 0.50
        + normalize_count(data.long_sessions_without_breaks, 5) * 0.50
    )
    return round(clamp01(score), 4)