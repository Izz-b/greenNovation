"""
LangGraph: orchestrator → learning.

The orchestrator is the main controller. It calls the specialist agents
(profile, RAG, readiness, energy), merges their outputs into AgentContext,
then hands off to the learning agent.
LangGraph: profile → readiness → energy → RAG → merge → learning.

Runs profile and readiness first, then energy (compute budget), retrieval,
a merged signal bundle for observability, and finally the learning agent.
"""

from __future__ import annotations

from typing import Any, Dict

from langgraph.graph import END, START, StateGraph

from ai.agents.energy.agent import energy_agent
from ai.agents.learning.agent import learning_agent
from ai.agents.orchestrator.agent import orchestrator_agent


async def orchestrator_step(state: Dict[str, Any]) -> Dict[str, Any]:
    patch = await orchestrator_agent(state)
    return {**state, **patch}


from ai.agents.profile.node import profile_agent_node
from ai.agents.rag.agent import rag_agent
from ai.agents.readiness.agent import run_readiness_agent


# =========================
# STEPS
# =========================

async def profile_step(state: Dict[str, Any]) -> Dict[str, Any]:
    patch = await profile_agent_node(state)
    return {**state, **patch}


def readiness_step(state: Dict[str, Any]) -> Dict[str, Any]:
    return {**state, **run_readiness_agent(state)}


def energy_step(state: Dict[str, Any]) -> Dict[str, Any]:
    return {**state, **energy_agent(state)}


def rag_step(state: Dict[str, Any]) -> Dict[str, Any]:
    return {**state, **rag_agent(state)}


def merge_signals_step(state: Dict[str, Any]) -> Dict[str, Any]:
    """Single bundle for downstream agents / logging (matches diagram intent)."""
    routing = state.get("routing") or {}
    energy = state.get("energy_decision") or {}
    readiness = state.get("readiness_signal") or {}
    profile = state.get("profile_vector") or {}
    chunks = state.get("retrieved_chunks") or []

    merged = {
        "intent": routing.get("intent", "unknown"),
        "energy_mode": energy.get("mode", "balanced"),
        "token_budget": energy.get("max_tokens", 400),
        "workload_pressure_score": readiness.get("workload_pressure_score"),
        "study_stability_score": readiness.get("study_stability_score"),
        "performance_trend_score": readiness.get("performance_trend_score"),
        "behavioral_fatigue_score": readiness.get("behavioral_fatigue_score"),
        "learning_vector": profile,
        "retrieved_chunks": chunks,
        "response_strategy": energy.get("reason", ""),
    }
    return {**state, "merged_signal_bundle": merged}


def merge_step(state: Dict[str, Any]) -> Dict[str, Any]:
    return merge_signals_step(state)


def learning_step(state: Dict[str, Any]) -> Dict[str, Any]:
    patch = learning_agent(state)
    return {**state, **patch}


# =========================
# DEBUG PIPELINE (optional)
# =========================

async def run_learning_pipeline(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Same sequence as the compiled LangGraph (orchestrator → learning),
    without going through the graph runtime.
    """
    state = {**state, **await orchestrator_agent(state)}
    Same sequence as the compiled LangGraph, without the graph runtime.
    """
    state = {**state, **await profile_agent_node(state)}
    state = {**state, **run_readiness_agent(state)}
    state = {**state, **energy_agent(state)}
    state = {**state, **rag_agent(state)}
    state = merge_signals_step(state)
    state = {**state, **learning_agent(state)}
    return state


# =========================
# GRAPH BUILDER
# =========================

def build_learning_graph():
    graph = StateGraph(dict)
    graph.add_node("orchestrator", orchestrator_step)
    graph.add_node("learning", learning_step)
    graph.add_edge(START, "orchestrator")
    graph.add_edge("orchestrator", "learning")
    graph.add_edge("learning", END)

    graph.add_node("profile", profile_step)
    graph.add_node("readiness", readiness_step)
    graph.add_node("energy", energy_step)
    graph.add_node("rag", rag_step)
    graph.add_node("merge", merge_step)
    graph.add_node("learning", learning_step)

    graph.add_edge(START, "profile")
    graph.add_edge("profile", "readiness")
    graph.add_edge("readiness", "energy")
    graph.add_edge("energy", "rag")
    graph.add_edge("rag", "merge")
    graph.add_edge("merge", "learning")
    graph.add_edge("learning", END)

    return graph.compile()