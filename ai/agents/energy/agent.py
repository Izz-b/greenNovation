from __future__ import annotations

from typing import Any, Dict


def _base_decision(
    mode: str,
    *,
    max_tokens: int,
    temperature: float,
    top_k: int,
    chunk_truncation_chars: int,
    generate_quiz: bool,
    include_sources: bool,
    response_depth: str,
    reason: str,
) -> Dict[str, Any]:
    return {
        "mode": mode,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "use_rag": True,
        "top_k": top_k,
        "chunk_truncation_chars": chunk_truncation_chars,
        "generate_quiz": generate_quiz,
        "include_sources": include_sources,
        "response_depth": response_depth,
        "use_profile": True,
        "use_readiness": True,
        "reason": reason,
    }


def energy_agent(state: dict) -> dict:
    """
    Energy-aware settings for RAG + learning, using intent + query + optional readiness.

    When the orchestrator runs energy *before* readiness in the same request,
    `readiness_signal` is usually empty: fatigue defaults apply for that turn.
    Readiness from a *previous* turn (carried in state) is still used when present.
    """
    query = state.get("query", "")
    intent = (state.get("routing") or {}).get("intent", "learn_concept")
    readiness = state.get("readiness_signal") or {}

    query_words = query.split()
    query_length = len(query_words)

    fatigue_band = readiness.get("behavioral_fatigue_band", "low")
    recommended = readiness.get("recommended_intensity", "normal")

    fatigue_high = fatigue_band == "high"
    recovery = recommended in ("light", "recovery_light")

    # ---- choose mode ----
    if fatigue_high or recovery:
        mode = "light"
        reason = "Readiness: high fatigue or recovery/light intensity → reduce load"
    elif intent == "practice":
        mode = "balanced"
        reason = "Practice intent → balanced retrieval and quiz-capable settings"
    elif query_length > 20:
        mode = "deep"
        reason = "Long query → deeper response"
    else:
        mode = "balanced"
        reason = "Default balanced session"

    # ---- map mode → full controls (RAG + LLM) ----
    if mode == "light":
        decision = _base_decision(
            "light",
            max_tokens=200,
            temperature=0.25,
            top_k=3,
            chunk_truncation_chars=400,
            generate_quiz=False,
            include_sources=False,
            response_depth="short",
            reason=reason,
        )
    elif mode == "deep":
        decision = _base_decision(
            "deep",
            max_tokens=800,
            temperature=0.35,
            top_k=8,
            chunk_truncation_chars=800,
            generate_quiz=True,
            include_sources=True,
            response_depth="long",
            reason=reason,
        )
    else:
        decision = _base_decision(
            "balanced",
            max_tokens=400,
            temperature=0.3,
            top_k=5,
            chunk_truncation_chars=600,
            generate_quiz=True,
            include_sources=True,
            response_depth="medium",
            reason=reason,
        )

    return {
        "energy_decision": decision,
        "agent_runs": {
            **state.get("agent_runs", {}),
            "energy_agent": {"status": "success"},
        },
    }
