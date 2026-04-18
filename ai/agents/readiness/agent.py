from __future__ import annotations

from ai.state.agent_context import AgentContext

from .rules import (
    build_reasoning_summary,
    choose_intensity,
    compute_risk_flags,
    select_top_risk_flags,
    to_band,
)
from .scoring import (
    compute_behavioral_fatigue_score,
    compute_performance_trend_score,
    compute_study_stability_score,
    compute_workload_pressure_score,
)
from .schemas import ReadinessInput, ReadinessOutput


def run_readiness_agent(state: AgentContext) -> AgentContext:
    try:
        passive_signals = state.get("passive_behavior_signals", {})
        data = ReadinessInput(**passive_signals)

        workload_pressure_score = compute_workload_pressure_score(data)
        study_stability_score = compute_study_stability_score(data)
        performance_trend_score = compute_performance_trend_score(data)
        behavioral_fatigue_score = compute_behavioral_fatigue_score(data)

        workload_pressure_band = to_band(workload_pressure_score)
        study_stability_band = to_band(study_stability_score)
        performance_trend_band = to_band(performance_trend_score)
        behavioral_fatigue_band = to_band(behavioral_fatigue_score)

        recommended_intensity, suggested_session_minutes = choose_intensity(
            workload_pressure_band=workload_pressure_band,
            study_stability_band=study_stability_band,
            performance_trend_band=performance_trend_band,
            behavioral_fatigue_band=behavioral_fatigue_band,
        )

        risk_flags = compute_risk_flags(
            data=data,
            workload_pressure_score=workload_pressure_score,
            study_stability_score=study_stability_score,
            performance_trend_score=performance_trend_score,
            behavioral_fatigue_score=behavioral_fatigue_score,
        )

        top_risk_flags = select_top_risk_flags(risk_flags)

        reasoning_summary = build_reasoning_summary(
            intensity=recommended_intensity,
            workload_pressure_band=workload_pressure_band,
            study_stability_band=study_stability_band,
            performance_trend_band=performance_trend_band,
            behavioral_fatigue_band=behavioral_fatigue_band,
            top_risk_flags=top_risk_flags,
        )

        output = ReadinessOutput(
            workload_pressure_score=workload_pressure_score,
            study_stability_score=study_stability_score,
            performance_trend_score=performance_trend_score,
            behavioral_fatigue_score=behavioral_fatigue_score,
            workload_pressure_band=workload_pressure_band,
            study_stability_band=study_stability_band,
            performance_trend_band=performance_trend_band,
            behavioral_fatigue_band=behavioral_fatigue_band,
            recommended_intensity=recommended_intensity,
            suggested_session_minutes=suggested_session_minutes,
            risk_flags=risk_flags,
            top_risk_flags=top_risk_flags,
            reasoning_summary=reasoning_summary,
        )

        state["readiness_signal"] = output.model_dump()

        state.setdefault("agent_runs", {})
        state["agent_runs"]["readiness_agent"] = {
            "status": "success",
        }

        state.setdefault("traces", [])
        state["traces"].append(
            {
                "agent": "readiness_agent",
                "event": "completed",
                "scores": {
                    "workload_pressure_score": workload_pressure_score,
                    "study_stability_score": study_stability_score,
                    "performance_trend_score": performance_trend_score,
                    "behavioral_fatigue_score": behavioral_fatigue_score,
                },
                "bands": {
                    "workload_pressure_band": workload_pressure_band,
                    "study_stability_band": study_stability_band,
                    "performance_trend_band": performance_trend_band,
                    "behavioral_fatigue_band": behavioral_fatigue_band,
                },
                "recommended_intensity": recommended_intensity,
                "suggested_session_minutes": suggested_session_minutes,
                "risk_flags": risk_flags,
                "top_risk_flags": top_risk_flags,
            }
        )

        return state

    except Exception as exc:
        state.setdefault("errors", [])
        state["errors"].append(f"readiness_agent_failed: {str(exc)}")

        state.setdefault("agent_runs", {})
        state["agent_runs"]["readiness_agent"] = {
            "status": "failed",
            "error": str(exc),
        }

        state.setdefault("traces", [])
        state["traces"].append(
            {
                "agent": "readiness_agent",
                "event": "failed",
                "error": str(exc),
            }
        )

        return state