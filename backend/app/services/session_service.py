from __future__ import annotations

import copy
from typing import Any

# Ephemeral keys not stored between HTTP turns
_EPHEMERAL = frozenset(
    {
        "traces",
        "retrieved_chunks",
        "merged_signal_bundle",
        "response_draft",
        "query",
        "final_response",
    }
)

_sessions: dict[str, dict[str, Any]] = {}


def default_session_state() -> dict[str, Any]:
    return {
        "session_history": [],
        "session_action": "continue",
        "conversation_summary": "",
        "readiness_signal": {"behavioral_fatigue_band": "low"},
        "calendar_events": [],
        "course_context": {},
        "agent_runs": {},
        "errors": [],
        "traces": [],
        "warnings": [],
        "metrics": {},
        "passive_behavior_signals": {
            "tasks_due_3d": 2,
            "overdue_tasks": 0,
            "project_risk_level": "low",
            "study_sessions_last_7d": 5,
            "avg_session_completion_rate": 0.8,
            "avg_quiz_score_trend": 4.0,
            "late_night_activity_ratio": 0.1,
            "long_sessions_without_breaks": 0,
        },
    }


def persistable_state(state: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(state)
    for k in _EPHEMERAL:
        out.pop(k, None)
    return out


def load_session_copy(session_id: str) -> dict[str, Any] | None:
    if session_id not in _sessions:
        return None
    return copy.deepcopy(_sessions[session_id])


def save_session(session_id: str, state: dict[str, Any]) -> None:
    _sessions[session_id] = persistable_state(state)


def delete_session(session_id: str) -> None:
    _sessions.pop(session_id, None)
