from __future__ import annotations

from typing import Any, Dict


def merge_metric_deltas(base: Dict[str, Any], deltas: Dict[str, int]) -> Dict[str, Any]:
    out = dict(base)
    for k, v in deltas.items():
        out[k] = int(out.get(k, 0) or 0) + int(v)
    return out


def energy_green_deltas(
    state: Dict[str, Any],
    decision: Dict[str, Any],
    *,
    has_answer_cache: bool,
    has_rag_cache: bool,
) -> Dict[str, int]:
    """
    Increment-only counters for hackathon / demo visibility.
    Estimates are rough order-of-magnitude, not billing-grade.
    """
    deltas: Dict[str, int] = {"green_energy_runs": 1}
    max_out = int(decision.get("max_tokens", 400) or 400)

    if has_answer_cache:
        deltas["green_answer_cache_hits"] = 1
        deltas["green_llm_calls_saved"] = 1
        deltas["green_rag_calls_saved"] = 1
        deltas["green_profile_calls_saved"] = 1
        deltas["green_readiness_calls_saved"] = 1
        deltas["green_estimated_tokens_saved"] = max_out + 1500
        return deltas

    est = 0

    if decision.get("reuse_cached_rag") and has_rag_cache and not decision.get("use_rag", True):
        deltas["green_rag_cache_hits"] = 1
        deltas["green_rag_calls_saved"] = 1
        est += 600

    if (
        decision.get("reuse_readiness_signal")
        and not decision.get("use_readiness", True)
        and bool(state.get("readiness_signal"))
    ):
        deltas["green_readiness_skips"] = 1
        deltas["green_readiness_calls_saved"] = 1
        est += 120

    if (
        decision.get("profile_ttl_ok")
        and bool(state.get("profile_vector"))
        and not decision.get("use_profile", True)
    ):
        deltas["green_profile_skips"] = 1
        deltas["green_profile_calls_saved"] = 1
        est += 800

    if est:
        deltas["green_estimated_tokens_saved"] = est

    return deltas


def learning_cache_hit_deltas() -> Dict[str, int]:
    """Learning served from full-answer cache (savings already counted in energy_green_deltas)."""
    return {"green_learning_cache_served": 1}
