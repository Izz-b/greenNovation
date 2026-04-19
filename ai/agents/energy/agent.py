from __future__ import annotations

from typing import Any, Dict

from ai.agents.energy.metrics import energy_green_deltas, merge_metric_deltas


def _normalize_query(query: str) -> str:
    q = " ".join((query or "").strip().lower().split())
    cleaned = "".join(ch for ch in q if ch.isalnum() or ch.isspace())
    return " ".join(cleaned.split())


def _build_cache_key(state: dict, intent: str, normalized_query: str) -> str:
    course_id = (
        (state.get("course_context") or {}).get("course_id")
        or (state.get("session_snapshot") or {}).get("current_course_id")
        or "global"
    )
    return f"{course_id}:{intent}:{normalized_query}"


def _profile_ttl_expired(state: dict, ttl_seconds: int = 7 * 24 * 3600) -> bool:
    import time

    cache = state.get("energy_cache") or {}
    last_ts = float(cache.get("profile_refreshed_at_ts", 0.0) or 0.0)
    if last_ts <= 0:
        return True
    return (time.time() - last_ts) > ttl_seconds


def _readiness_changed_significantly(state: dict) -> bool:
    cache = state.get("energy_cache") or {}
    prev = cache.get("last_readiness_input") or {}
    curr = state.get("passive_behavior_signals") or {}
    if not prev:
        return True
    if int(curr.get("tasks_due_3d", 0)) != int(prev.get("tasks_due_3d", 0)):
        return True
    if int(curr.get("overdue_tasks", 0)) != int(prev.get("overdue_tasks", 0)):
        return True
    if curr.get("project_risk_level", "low") != prev.get("project_risk_level", "low"):
        return True
    if abs(float(curr.get("avg_session_completion_rate", 0.0)) - float(prev.get("avg_session_completion_rate", 0.0))) >= 0.05:
        return True
    if abs(float(curr.get("avg_quiz_score_trend", 0.0)) - float(prev.get("avg_quiz_score_trend", 0.0))) >= 2.0:
        return True
    if abs(float(curr.get("late_night_activity_ratio", 0.0)) - float(prev.get("late_night_activity_ratio", 0.0))) >= 0.1:
        return True
    if int(curr.get("long_sessions_without_breaks", 0)) != int(prev.get("long_sessions_without_breaks", 0)):
        return True
    return False


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
    cache = state.get("energy_cache") or {}

    query_words = query.split()
    query_length = len(query_words)
    normalized_query = _normalize_query(query)
    cache_key = _build_cache_key(state, intent, normalized_query)
    answer_cache = cache.get("answer_cache") or {}
    rag_cache = cache.get("rag_cache") or {}
    cached_answer = answer_cache.get(cache_key)
    cached_rag_chunks = rag_cache.get(cache_key)
    has_answer_cache = cached_answer is not None
    has_rag_cache = isinstance(cached_rag_chunks, list) and len(cached_rag_chunks) > 0

    readiness_changed = _readiness_changed_significantly(state)
    reuse_readiness_signal = (not readiness_changed) and bool(state.get("readiness_signal"))
    profile_ttl_expired = _profile_ttl_expired(state)

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

    decision.update(
        {
            "reuse_cached_answer": has_answer_cache,
            "reuse_cached_rag": (not has_answer_cache) and has_rag_cache,
            "reuse_readiness_signal": reuse_readiness_signal,
            "readiness_inputs_unchanged": not readiness_changed,
            "profile_ttl_ok": not profile_ttl_expired,
            "cache_key": cache_key,
        }
    )

    # Reuse policy can override expensive paths.
    if has_answer_cache:
        decision["use_rag"] = False
        decision["use_profile"] = False
        decision["use_readiness"] = False
        decision["reason"] = "Exact cache hit: reused final answer and skipped specialist agents"
    else:
        if has_rag_cache:
            decision["use_rag"] = False
            decision["reason"] = f"{decision['reason']}; reused cached retrieval chunks"
        if reuse_readiness_signal:
            decision["use_readiness"] = False
            decision["reason"] = f"{decision['reason']}; readiness inputs unchanged"
        if not profile_ttl_expired and bool(state.get("profile_vector")):
            decision["use_profile"] = False
            decision["reason"] = f"{decision['reason']}; profile TTL still valid"

    metrics = merge_metric_deltas(
        dict(state.get("metrics") or {}),
        energy_green_deltas(
            state,
            decision,
            has_answer_cache=has_answer_cache,
            has_rag_cache=has_rag_cache,
        ),
    )

    return {
        "energy_decision": decision,
        "cached_answer": cached_answer,
        "cached_rag_chunks": cached_rag_chunks if has_rag_cache else [],
        "metrics": metrics,
        "agent_runs": {
            **state.get("agent_runs", {}),
            "energy_agent": {"status": "success"},
        },
    }
