"""
LangGraph: orchestrator → learning [→ planning when session ends].

Inside the orchestrator: intent → energy → parallel fan-out (profile, RAG,
readiness) → merge bundle → return. See `ai.agents.orchestrator.agent`.

The outer graph keeps specialist work inside one orchestrator node so agents
are not double-invoked; the learning node produces the user-facing reply.
"""

from __future__ import annotations

from typing import Any, Dict
from datetime import datetime
from langgraph.graph import END, START, StateGraph

from ai.agents.learning.agent import learning_agent
from ai.agents.orchestrator.agent import orchestrator_agent
from ai.agents.planner.agent import planning_agent
from ai.agents.planner.agent import should_run_planner


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
def planning_step(state: dict) -> dict:
    """
    Runs planner ONLY once per day (or if forced).
    """

    planner_state = state.get("planner_state", {
        "last_generated_date": None,
        "turns_since_last_plan": 0
    })

    # increment turns
    planner_state["turns_since_last_plan"] += 1

    if not should_run_planner(state):
        return {
            "planner_state": planner_state,
            "agent_runs": {
                **state.get("agent_runs", {}),
                "planning_agent": {
                    "status": "skipped"
                }
            }
        }

    # ✅ Run planner
    result = planning_agent(state)

    planner_state["last_generated_date"] = datetime.utcnow().isoformat()
    planner_state["turns_since_last_plan"] = 0

    return {
        **result,
        "planner_state": planner_state
    }
def route_after_learning(state: Dict[str, Any]) -> str:
    action = state.get("session_action", "continue")
    if action == "stop":
        return "planning"
    return END
def build_learning_graph():
    """Single path: orchestrator (all specialist agents) → learning → end."""
    graph = StateGraph(dict)
    graph.add_node("orchestrator", orchestrator_step)
    graph.add_node("learning", learning_step)
    graph.add_node("planning", planning_step)

    graph.add_edge(START, "orchestrator")
    graph.add_edge("orchestrator", "learning")
    graph.add_conditional_edges(
        "learning",
        route_after_learning,
        {
            "planning": "planning",
            END: END,
        },
    )    
    graph.add_edge("planning", END)

    return graph.compile()
