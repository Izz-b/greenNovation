from __future__ import annotations

from typing import Any, Dict


def choose_response_strategy(
    intent: str,
    profile_vector: Dict[str, Any],
    session_signals: Dict[str, Any],
) -> str:
    preferred_format = profile_vector.get("preferred_format", "")
    struggle_score = float(
        session_signals.get("struggle_score", session_signals.get("stress_score", 0.0))
    )

    if intent == "practice":
        return "exercise_first"
    if intent == "revise":
        return "summary_first"
    if intent == "plan_study":
        return "structured_plan"
    if struggle_score >= 0.7:
        return "scaffolded_explanation"
    if preferred_format == "examples_first":
        return "examples_first"

    return "guided_explanation"


def merge_outputs(state: Dict[str, Any]) -> Dict[str, Any]:
    routing = state.get("routing", {})
    intent = routing.get("intent", "unknown")

    profile_vector = state.get("profile_vector", {})
    retrieved_chunks = state.get("retrieved_chunks", [])
    session_signals = state.get("session_signals", {})
    energy_decision = state.get("energy_decision", {})

    response_strategy = choose_response_strategy(
        intent=intent,
        profile_vector=profile_vector,
        session_signals=session_signals,
    )

    merged_signal_bundle = {
        "intent": intent,
        "retrieved_chunks": retrieved_chunks,
        "profile_vector": profile_vector,
        "session_signals": session_signals,
        "energy_decision": energy_decision,
        "response_strategy": response_strategy,
    }

    response_draft = {
        "answer_type": (
            "exercise" if intent == "practice"
            else "summary" if intent == "revise"
            else "plan" if intent == "plan_study"
            else "supportive_guidance" if intent == "wellbeing_check"
            else "explanation"
        ),
        "structure": response_strategy,
        "tone": "supportive" if intent in {"wellbeing_check", "mixed"} else "clear",
        "key_points": [],
    }

    return {
        "merged_signal_bundle": merged_signal_bundle,
        "response_draft": response_draft,
    }