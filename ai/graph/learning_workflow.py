from __future__ import annotations

from typing import Any, Dict

from langgraph.graph import END, START, StateGraph

from ai.agents.learning.agent import learning_agent
from ai.agents.profile.node import profile_agent_node
from ai.agents.rag.agent import rag_agent
from ai.agents.energy.agent import energy_agent   


# =========================
# STEPS
# =========================

async def profile_step(state: Dict[str, Any]) -> Dict[str, Any]:
    patch = await profile_agent_node(state)
    return {**state, **patch}


def energy_step(state: Dict[str, Any]) -> Dict[str, Any]:
    return {**state, **energy_agent(state)}   


def rag_step(state: Dict[str, Any]) -> Dict[str, Any]:
    return {**state, **rag_agent(state)}


def learning_step(state: Dict[str, Any]) -> Dict[str, Any]:
    return {**state, **learning_agent(state)}


# =========================
# DEBUG PIPELINE (optional)
# =========================

async def run_learning_pipeline(state: Dict[str, Any]) -> Dict[str, Any]:
    state = {**state, **await profile_agent_node(state)}
    state = {**state, **energy_agent(state)}     
    state = {**state, **rag_agent(state)}
    state = {**state, **learning_agent(state)}
    return state


# =========================
# GRAPH BUILDER
# =========================

def build_learning_graph():
    graph = StateGraph(dict)

    graph.add_node("profile", profile_step)
    graph.add_node("energy", energy_step)   
    graph.add_node("rag", rag_step)
    graph.add_node("learning", learning_step)

    # FLOW
    graph.add_edge(START, "profile")
    graph.add_edge("profile", "energy")     
    graph.add_edge("energy", "rag")         
    graph.add_edge("rag", "learning")
    graph.add_edge("learning", END)

    return graph.compile()