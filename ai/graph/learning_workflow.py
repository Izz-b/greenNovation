"""
LangGraph: orchestrator → learning.

The orchestrator classifies intent, runs energy (first), then conditionally runs
profile, RAG, and readiness, and merges context for the learning step
(see `ai.agents.orchestrator.agent`).

The compiled graph only needs two nodes: specialist work runs inside the
orchestrator; the learning node produces the final response. This matches
`ai.agents.orchestrator.graph` and avoids double-invoking agents.
"""

from __future__ import annotations

from typing import Any, Dict

from langgraph.graph import END, START, StateGraph

from ai.agents.learning.agent import learning_agent
from ai.agents.orchestrator.agent import orchestrator_agent


async def orchestrator_step(state: Dict[str, Any]) -> Dict[str, Any]:
    patch = await orchestrator_agent(state)
    return {**state, **patch}


def learning_step(state: Dict[str, Any]) -> Dict[str, Any]:
    patch = learning_agent(state)
    return {**state, **patch}


async def run_learning_pipeline(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Same sequence as `build_learning_graph().compile()` (orchestrator then learning),
    without the LangGraph runtime.
    """
    state = {**state, **await orchestrator_agent(state)}
    state = {**state, **learning_agent(state)}
    return state


def build_learning_graph():
    """Single path: orchestrator (all specialist agents) → learning → end."""
    graph = StateGraph(dict)
    graph.add_node("orchestrator", orchestrator_step)
    graph.add_node("learning", learning_step)
    graph.add_edge(START, "orchestrator")
    graph.add_edge("orchestrator", "learning")
    graph.add_edge("learning", END)
    return graph.compile()
