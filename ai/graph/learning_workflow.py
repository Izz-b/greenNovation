"""
LangGraph: orchestrator → learning.

The orchestrator is the main controller. It calls the specialist agents
(profile, RAG, readiness, energy), merges their outputs into AgentContext,
then hands off to the learning agent.
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
    Same sequence as the compiled LangGraph (orchestrator → learning),
    without going through the graph runtime.
    """
    state = {**state, **await orchestrator_agent(state)}
    state = {**state, **learning_agent(state)}
    return state


def build_learning_graph():
    graph = StateGraph(dict)
    graph.add_node("orchestrator", orchestrator_step)
    graph.add_node("learning", learning_step)
    graph.add_edge(START, "orchestrator")
    graph.add_edge("orchestrator", "learning")
    graph.add_edge("learning", END)
    return graph.compile()