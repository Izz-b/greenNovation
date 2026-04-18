"""
LangGraph: profile → RAG → learning.

Compiles a graph that runs the profile agent first so `profile_vector`
is available when the learning agent builds its prompt.
"""

from __future__ import annotations

from typing import Any, Dict

from langgraph.graph import END, START, StateGraph

from ai.agents.learning.agent import learning_agent
from ai.agents.profile.node import profile_agent_node
from ai.agents.rag.agent import rag_agent


async def profile_step(state: Dict[str, Any]) -> Dict[str, Any]:
    patch = await profile_agent_node(state)
    return {**state, **patch}


def rag_step(state: Dict[str, Any]) -> Dict[str, Any]:
    return {**state, **rag_agent(state)}


def learning_step(state: Dict[str, Any]) -> Dict[str, Any]:
    return {**state, **learning_agent(state)}


async def run_learning_pipeline(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Same sequence as the compiled LangGraph (profile → RAG → learning),
    without going through the graph runtime. Useful for debugging or if
    LangGraph is unavailable.
    """
    state = {**state, **await profile_agent_node(state)}
    state = {**state, **rag_agent(state)}
    state = {**state, **learning_agent(state)}
    return state


def build_learning_graph():
    graph = StateGraph(dict)
    graph.add_node("profile", profile_step)
    graph.add_node("rag", rag_step)
    graph.add_node("learning", learning_step)
    graph.add_edge(START, "profile")
    graph.add_edge("profile", "rag")
    graph.add_edge("rag", "learning")
    graph.add_edge("learning", END)
    return graph.compile()
