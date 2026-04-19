from __future__ import annotations

from typing import Any, Dict, List, Optional

from ai.state.agent_context import AgentContext


def build_initial_context(
    query: str,
    user_profile: Optional[Dict[str, Any]] = None,
    session_history: Optional[List[Dict[str, Any]]] = None,
    session_snapshot: Optional[Dict[str, Any]] = None,
    course_context: Optional[Dict[str, Any]] = None,
    concept_graph: Optional[Dict[str, Any]] = None,
) -> AgentContext:
    """
    Build a clean initial AgentContext for a new LangGraph run.
    """

    clean_query = (query or "").strip()
    if not clean_query:
        raise ValueError("query must not be empty")

    context: AgentContext = {
        # ---- request/session input ----
        "query": clean_query,
        "user_profile": user_profile or {},
        "session_history": session_history or [],
        "session_snapshot": session_snapshot or {},
        "course_context": course_context or {},
        "concept_graph": concept_graph or {},

        # ---- orchestrator-owned ----
        "routing": {},

        # ---- agent namespaces ----
        "retrieval_query": {},
        "retrieved_chunks": [],
        "profile_vector": {},
        "session_signals": {},
        "energy_decision": {},
        "energy_cache": {
            "answer_cache": {},
            "rag_cache": {},
            "last_readiness_input": {},
            "profile_refreshed_at_ts": 0.0,
        },

        # ---- merged output ----
        "merged_signal_bundle": {},
        "response_draft": {},

        # ---- downstream/final ----
        "final_response": "",
        "planning_task": {},

        # ---- observability ----
        "warnings": [],
        "errors": [],
        "traces": [],
        "metrics": {},
        "agent_runs": {},
    }

    return context