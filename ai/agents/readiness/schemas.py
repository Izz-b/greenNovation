from __future__ import annotations

from typing import Literal, List, Optional

from pydantic import BaseModel, Field, field_validator


RiskLevel = Literal["low", "medium", "high"]
BandLevel = Literal["low", "medium", "high"]
RecommendedIntensity = Literal["light", "normal", "full", "recovery_light"]
DifficultyAdjustment = Literal["decrease", "keep", "increase"]
SupportTone = Literal["supportive", "neutral", "challenging"]


class ReadinessInput(BaseModel):
    # 1) Workload pressure
    tasks_due_3d: int = Field(default=0, ge=0)
    overdue_tasks: int = Field(default=0, ge=0)
    project_risk_level: RiskLevel = "low"

    # 2) Study stability
    study_sessions_last_7d: int = Field(default=0, ge=0)
    avg_session_completion_rate: float = Field(default=0.0, ge=0.0, le=1.0)

    # 3) Performance trend
    avg_quiz_score_trend: float = 0.0

    # 4) Behavioral fatigue
    late_night_activity_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    long_sessions_without_breaks: int = Field(default=0, ge=0)


class ReadinessOutput(BaseModel):
    workload_pressure_score: float = Field(ge=0.0, le=1.0)
    study_stability_score: float = Field(ge=0.0, le=1.0)
    performance_trend_score: float = Field(ge=0.0, le=1.0)
    behavioral_fatigue_score: float = Field(ge=0.0, le=1.0)

    workload_pressure_band: BandLevel
    study_stability_band: BandLevel
    performance_trend_band: BandLevel
    behavioral_fatigue_band: BandLevel

    recommended_intensity: RecommendedIntensity
    suggested_session_minutes: int = Field(ge=10, le=90)

    # MVP adaptation controls for Learning Plan agent
    difficulty_adjustment: DifficultyAdjustment
    break_recommendation: bool
    support_tone: SupportTone

    risk_flags: List[str] = Field(default_factory=list)
    top_risk_flags: List[str] = Field(default_factory=list)
    reasoning_summary: str


class ReadinessAgentResult(BaseModel):
    status: Literal["success", "failed"]
    signal: Optional[ReadinessOutput] = None
    error: Optional[str] = None

    @field_validator("error")
    @classmethod
    def validate_error(cls, value: Optional[str], info):
        status = info.data.get("status")
        if status == "failed" and not value:
            raise ValueError("error is required when status='failed'")
        return value