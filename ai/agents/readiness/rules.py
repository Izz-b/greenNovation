from __future__ import annotations

from .schemas import ReadinessInput


def to_band(score: float) -> str:
    if score < 0.40:
        return "low"
    if score < 0.70:
        return "medium"
    return "high"


def choose_intensity(
    workload_pressure_band: str,
    study_stability_band: str,
    performance_trend_band: str,
    behavioral_fatigue_band: str,
) -> tuple[str, int]:
    if workload_pressure_band == "high" and behavioral_fatigue_band == "high":
        return "recovery_light", 15

    if workload_pressure_band == "high":
        return "light", 20

    if behavioral_fatigue_band == "high":
        return "light", 20

    if study_stability_band == "low" and performance_trend_band == "high":
        return "light", 20

    if (
        workload_pressure_band == "low"
        and study_stability_band == "high"
        and performance_trend_band == "low"
        and behavioral_fatigue_band == "low"
    ):
        return "full", 45

    return "normal", 30


def derive_adaptation_controls(recommended_intensity: str) -> tuple[str, bool, str]:
    """
    Returns:
    - difficulty_adjustment
    - break_recommendation
    - support_tone
    """
    if recommended_intensity == "recovery_light":
        return "decrease", True, "supportive"

    if recommended_intensity == "light":
        return "decrease", True, "supportive"

    if recommended_intensity == "normal":
        return "keep", False, "neutral"

    return "increase", False, "challenging"


def compute_risk_flags(
    data: ReadinessInput,
    workload_pressure_score: float,
    study_stability_score: float,
    performance_trend_score: float,
    behavioral_fatigue_score: float,
) -> list[str]:
    flags: list[str] = []

    if data.tasks_due_3d >= 3:
        flags.append("multiple_near_deadlines")
    if data.overdue_tasks > 0:
        flags.append("overdue_work_present")
    if data.project_risk_level == "high":
        flags.append("high_project_risk")

    if data.study_sessions_last_7d <= 2:
        flags.append("low_study_consistency")
    if data.avg_session_completion_rate < 0.60:
        flags.append("low_session_completion")

    if data.avg_quiz_score_trend <= -8:
        flags.append("declining_learning_trend")

    if data.late_night_activity_ratio >= 0.40:
        flags.append("late_night_study_pattern")
    if data.long_sessions_without_breaks >= 2:
        flags.append("long_sessions_without_breaks")

    if workload_pressure_score >= 0.70:
        flags.append("high_workload_pressure")
    if study_stability_score < 0.40:
        flags.append("unstable_study_pattern")
    if performance_trend_score >= 0.70:
        flags.append("high_academic_struggle")
    if behavioral_fatigue_score >= 0.70:
        flags.append("fatigue_pattern_detected")

    return flags


def select_top_risk_flags(flags: list[str]) -> list[str]:
    priority = [
        "high_workload_pressure",
        "declining_learning_trend",
        "fatigue_pattern_detected",
        "unstable_study_pattern",
        "multiple_near_deadlines",
        "overdue_work_present",
        "high_project_risk",
        "low_session_completion",
        "late_night_study_pattern",
        "long_sessions_without_breaks",
        "high_academic_struggle",
        "low_study_consistency",
    ]

    selected: list[str] = []

    for item in priority:
        if item in flags and item not in selected:
            selected.append(item)
        if len(selected) == 3:
            return selected

    for item in flags:
        if item not in selected:
            selected.append(item)
        if len(selected) == 3:
            break

    return selected


def build_reasoning_summary(
    intensity: str,
    workload_pressure_band: str,
    study_stability_band: str,
    performance_trend_band: str,
    behavioral_fatigue_band: str,
    top_risk_flags: list[str],
) -> str:
    reasons: list[str] = []

    if workload_pressure_band == "high":
        reasons.append("high workload pressure")
    if study_stability_band == "low":
        reasons.append("low study stability")
    if performance_trend_band == "high":
        reasons.append("academic struggle signals")
    if behavioral_fatigue_band == "high":
        reasons.append("behavioral fatigue signals")

    if not reasons and top_risk_flags:
        reasons = top_risk_flags[:2]

    if intensity == "recovery_light":
        if reasons:
            return f"A recovery-focused light session is recommended due to {', '.join(reasons)}."
        return "A recovery-focused light session is recommended."

    if intensity == "light":
        if reasons:
            return f"A lighter and more focused study session is recommended due to {', '.join(reasons)}."
        return "A lighter and more focused study session is recommended."

    if intensity == "full":
        return "Your current patterns look stable enough for a deeper study session."

    if reasons:
        return f"A balanced study session is recommended while monitoring {', '.join(reasons)}."

    return "A balanced study session is recommended based on current learning patterns."