from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from ai.agents.profile.node import profile_agent_node
from ai.agents.rag.agent import rag_agent
from ai.agents.readiness.agent import readiness_agent
from ai.agents.energy.agent import energy_agent


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _classify_intent(query: str, fallback_intent: str = "unknown") -> tuple[str, str]:
    q = (query or "").strip().lower()

    if fallback_intent and fallback_intent != "unknown":
        return fallback_intent, "Intent provided by upstream state."

    if any(k in q for k in ["exercise", "exercises", "practice", "quiz", "problems"]):
        return "practice", "Practice-oriented wording detected."
    if any(k in q for k in ["revise", "revision", "review", "summary", "summarize"]):
        return "revise", "Revision-oriented wording detected."
    if any(k in q for k in ["plan", "schedule", "roadmap", "study plan"]):
        return "plan_study", "Planning-oriented wording detected."
    if any(k in q for k in ["stress", "stressed", "overwhelmed", "anxious", "burnout"]):
        return "wellbeing_check", "Wellbeing wording detected."
    if any(k in q for k in ["explain", "what is", "teach me", "help me understand"]):
        return "learn_concept", "Concept-learning wording detected."

    return "unknown", "No strong intent detected."


def _build_base_routing(intent: str, route_reason: str) -> Dict[str, Any]:
    priority = "normal"
    if intent in {"wellbeing_check", "mixed"}:
        priority = "high"

    return {
        "intent": intent,
        "requested_agents": [],
        "route_reason": route_reason,
        "priority": priority,
        "token_budget": 0,
    }


def _build_execution_plan(intent: str, energy_decision: Dict[str, Any]) -> Dict[str, Any]:
    requested_agents = []

    if energy_decision.get("use_profile", False):
        requested_agents.append("profile")

    if energy_decision.get("use_rag", False) and intent not in {"wellbeing_check"}:
        requested_agents.append("rag")

    if energy_decision.get("use_readiness", False):
        requested_agents.append("readiness")

    token_budget = int(energy_decision.get("max_tokens", 400))

    return {
        "requested_agents": requested_agents,
        "token_budget": token_budget,
        "response_depth": energy_decision.get("response_depth", "medium"),
    }


def _merge_outputs(state: Dict[str, Any]) -> Dict[str, Any]:
    routing = state.get("routing", {})
    intent = routing.get("intent", "unknown")

    profile_vector = state.get("profile_vector", {})
    retrieved_chunks = state.get("retrieved_chunks", [])
    readiness_signal = state.get("readiness_signal", {}) or state.get("session_signals", {})
    energy_decision = state.get("energy_decision", {})

    preferred_format = profile_vector.get("preferred_format", "")
    struggle_score = float(
        readiness_signal.get("struggle_score", readiness_signal.get("stress_score", 0.0))
    )

    if intent == "practice":
        response_strategy = "exercise_first"
    elif intent == "revise":
        response_strategy = "summary_first"
    elif intent == "plan_study":
        response_strategy = "structured_plan"
    elif struggle_score >= 0.7:
        response_strategy = "scaffolded_explanation"
    elif preferred_format == "examples_first":
        response_strategy = "examples_first"
    else:
        response_strategy = "guided_explanation"

    merged_signal_bundle = {
        "intent": intent,
        "retrieved_chunks": retrieved_chunks,
        "profile_vector": profile_vector,
        "readiness_signal": readiness_signal,
        "energy_decision": energy_decision,
        "response_strategy": response_strategy,
    }

    response_draft = {
        "answer_type": (
            "exercise" if intent == "practice"
            else "summary_with_questions" if intent == "revise"
            else "plan" if intent == "plan_study"
            else "supportive_guidance" if intent == "wellbeing_check"
            else "explanation"
        ),
        "structure": "contextual_rag" if retrieved_chunks else response_strategy,
        "tone": "adaptive",
    }

    return {
        "merged_signal_bundle": merged_signal_bundle,
        "response_draft": response_draft,
    }


async def orchestrator_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    started_at = _utc_now()

    try:
        query = state.get("query", "")
        fallback_intent = state.get("routing", {}).get("intent", "unknown")

        intent, route_reason = _classify_intent(query, fallback_intent=fallback_intent)
        routing = _build_base_routing(intent, route_reason)

        updates: Dict[str, Any] = {
            "routing": routing,
            "traces": [
                {
                    "agent": "orchestrator",
                    "message": f"intent={intent}; starting energy-first orchestration",
                }
            ],
        }

        # 1) ENERGY FIRST
        energy_patch = energy_agent({**state, **updates})
        updates.update(energy_patch)

        energy_decision = updates.get("energy_decision", state.get("energy_decision", {}))
        execution_plan = _build_execution_plan(intent, energy_decision)

        updates["routing"] = {
            **routing,
            "requested_agents": execution_plan["requested_agents"],
            "token_budget": execution_plan["token_budget"],
        }

        working_state = {**state, **updates}
        requested = execution_plan["requested_agents"]

        # 2) CONDITIONAL AGENTS BASED ON ENERGY
        if "profile" in requested:
            profile_patch = await profile_agent_node(working_state)
            updates.update(profile_patch)
            working_state = {**working_state, **profile_patch}

        if "rag" in requested:
            rag_patch = rag_agent(working_state)
            updates.update(rag_patch)
            working_state = {**working_state, **rag_patch}

        if "readiness" in requested:
            readiness_patch = readiness_agent(working_state)
            updates.update(readiness_patch)
            working_state = {**working_state, **readiness_patch}

        # 3) MERGE
        merged_patch = _merge_outputs({**state, **updates})
        updates.update(merged_patch)

        existing_runs = updates.get("agent_runs", {})
        existing_runs["orchestrator"] = {
            "status": "success",
            "started_at": started_at,
            "finished_at": _utc_now(),
        }
        updates["agent_runs"] = existing_runs

        updates.setdefault("traces", [])
        updates["traces"].append(
            {
                "agent": "orchestrator",
                "message": (
                    f"energy_mode={energy_decision.get('mode', 'unknown')}; "
                    f"requested_agents={execution_plan['requested_agents']}"
                ),
            }
        )

        return updates

    except Exception as exc:
        return {
            "warnings": [f"orchestrator failed: {exc}"],
            "agent_runs": {
                "orchestrator": {
                    "status": "failed",
                    "started_at": started_at,
                    "finished_at": _utc_now(),
                    "error": str(exc),
                }
            },
        }