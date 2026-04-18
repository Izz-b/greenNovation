from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from ai.agents.orchestrator.adapters import call_learning_agent
from ai.agents.orchestrator.agent import orchestrator_agent
from ai.state.agent_context import AgentContext


def build_graph():
    builder = StateGraph(AgentContext)

    builder.add_node("orchestrator", orchestrator_agent)
    builder.add_node("learning", call_learning_agent)

    builder.add_edge(START, "orchestrator")
    builder.add_edge("orchestrator", "learning")
    builder.add_edge("learning", END)

    return builder.compile()


graph = build_graph()