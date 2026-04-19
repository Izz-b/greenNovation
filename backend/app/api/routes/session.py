from __future__ import annotations

from fastapi import APIRouter

from ai.agents.planner.agent import planning_agent

from backend.app.services import session_service as sessions

router = APIRouter(tags=["session"])


@router.post("/api/session/{session_id}/end")
def end_session_run_planner(session_id: str) -> dict:
    """
    Run the planning agent on the current session context, then delete the session.

    Used when the learner explicitly ends a study session from the workspace so the
    planner can summarize the block and propose the next session (force_planner).
    """
    base = sessions.load_session_copy(session_id) or sessions.default_session_state()
    base["force_planner"] = True
    base["session_action"] = "stop"

    result = planning_agent(base)
    planning_task = result.get("planning_task")
    planner_state = result.get("planner_state")
    agent_run = (result.get("agent_runs") or {}).get("planning_agent") or {}
    status = str(agent_run.get("status", "unknown"))

    sessions.store_planning_after_session_end(
        {
            "session_id_ended": session_id,
            "planning_task": planning_task,
            "planner_state": planner_state,
            "planning_agent": agent_run,
            "errors": result.get("errors"),
        }
    )
    sessions.delete_session(session_id)

    return {
        "ok": True,
        "planner": {
            "status": status,
            "skipped": status == "skipped",
            "reason": agent_run.get("reason"),
            "planning_task": planning_task,
        },
    }


@router.delete("/api/session/{session_id}")
def clear_session(session_id: str):
    sessions.delete_session(session_id)
    return {"ok": True}
