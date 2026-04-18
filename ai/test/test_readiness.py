from ai.agents.readiness.agent import run_readiness_agent
import json


def test_show_readiness_response():
    state = {
        "passive_behavior_signals": {
            "tasks_due_3d": 4,
            "overdue_tasks": 1,
            "project_risk_level": "high",
            "study_sessions_last_7d": 3,
            "avg_session_completion_rate": 0.55,
            "avg_quiz_score_trend": -10,
            "late_night_activity_ratio": 0.5,
            "long_sessions_without_breaks": 3,
        },
        "agent_runs": {},
        "traces": [],
        "errors": [],
    }

    result = run_readiness_agent(state)

    print("\nREADINESS SIGNAL:")
    print(json.dumps(result["readiness_signal"], indent=2))

    assert "readiness_signal" in result


def test_readiness_agent_returns_signal():
    state = {
        "passive_behavior_signals": {
            "tasks_due_3d": 4,
            "overdue_tasks": 1,
            "project_risk_level": "high",
            "study_sessions_last_7d": 3,
            "avg_session_completion_rate": 0.55,
            "avg_quiz_score_trend": -10,
            "late_night_activity_ratio": 0.5,
            "long_sessions_without_breaks": 3,
        },
        "agent_runs": {},
        "traces": [],
        "errors": [],
    }

    result = run_readiness_agent(state)
    signal = result["readiness_signal"]

    assert "workload_pressure_score" in signal
    assert "study_stability_score" in signal
    assert "performance_trend_score" in signal
    assert "behavioral_fatigue_score" in signal

    assert "workload_pressure_band" in signal
    assert "study_stability_band" in signal
    assert "performance_trend_band" in signal
    assert "behavioral_fatigue_band" in signal

    assert "recommended_intensity" in signal
    assert "suggested_session_minutes" in signal
    assert "risk_flags" in signal
    assert "top_risk_flags" in signal
    assert "reasoning_summary" in signal

    assert len(signal["top_risk_flags"]) <= 3
    assert result["agent_runs"]["readiness_agent"]["status"] == "success"
    assert len(result["traces"]) > 0


def test_readiness_agent_handles_empty_input():
    state = {
        "passive_behavior_signals": {},
        "agent_runs": {},
        "traces": [],
        "errors": [],
    }

    result = run_readiness_agent(state)

    assert "readiness_signal" in result
    assert result["agent_runs"]["readiness_agent"]["status"] == "success"


def test_readiness_agent_detects_high_pressure_case():
    state = {
        "passive_behavior_signals": {
            "tasks_due_3d": 5,
            "overdue_tasks": 3,
            "project_risk_level": "high",
            "study_sessions_last_7d": 2,
            "avg_session_completion_rate": 0.4,
            "avg_quiz_score_trend": -15,
            "late_night_activity_ratio": 0.7,
            "long_sessions_without_breaks": 4,
        },
        "agent_runs": {},
        "traces": [],
        "errors": [],
    }

    result = run_readiness_agent(state)
    signal = result["readiness_signal"]

    assert signal["workload_pressure_band"] in ["medium", "high"]
    assert signal["performance_trend_band"] in ["medium", "high"]
    assert signal["behavioral_fatigue_band"] in ["medium", "high"]
    assert signal["recommended_intensity"] in ["light", "recovery_light"]


def test_readiness_agent_detects_stable_case():
    state = {
        "passive_behavior_signals": {
            "tasks_due_3d": 0,
            "overdue_tasks": 0,
            "project_risk_level": "low",
            "study_sessions_last_7d": 6,
            "avg_session_completion_rate": 0.9,
            "avg_quiz_score_trend": 5,
            "late_night_activity_ratio": 0.1,
            "long_sessions_without_breaks": 0,
        },
        "agent_runs": {},
        "traces": [],
        "errors": [],
    }

    result = run_readiness_agent(state)
    signal = result["readiness_signal"]

    assert signal["recommended_intensity"] in ["normal", "full"]
    assert signal["workload_pressure_band"] == "low"