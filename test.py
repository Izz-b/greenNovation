import asyncio
import json
import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from ai.agents.profile.schema import ProfileInference
from ai.graph.learning_workflow import build_learning_graph


# =========================
# INITIAL STATE (PERSISTENT)
# =========================

state = {
    "session_history": [],
    "session_action": "continue",
    "conversation_summary": "",
    "readiness_signal": {
        "behavioral_fatigue_band": "low"
    },
    "calendar_events": [
        {
            "title": "Math exam",
            "date": "2026-04-20",
            "priority": "high"
        },
        {
            "title": "AI project deadline",
            "date": "2026-04-22",
            "priority": "high"
        }
    ],
    "course_context": {},
    "agent_runs": {},
    "errors": [],
    "traces": [],
    "warnings": [],
}


# =========================
# TWO STUDY TURNS ONLY
# =========================

queries = [
    ("learn_concept", "What is a decorator in python?"),
    ("practice", "Give me exercises on it"),
]

readiness_scenarios = [
    {
        "tasks_due_3d": 2,
        "overdue_tasks": 0,
        "project_risk_level": "low",
        "study_sessions_last_7d": 5,
        "avg_session_completion_rate": 0.8,
        "avg_quiz_score_trend": 4.0,
        "late_night_activity_ratio": 0.1,
        "long_sessions_without_breaks": 0,
    },
    {
        "tasks_due_3d": 5,
        "overdue_tasks": 1,
        "project_risk_level": "medium",
        "study_sessions_last_7d": 3,
        "avg_session_completion_rate": 0.6,
        "avg_quiz_score_trend": -2.0,
        "late_night_activity_ratio": 0.45,
        "long_sessions_without_breaks": 2,
    },
]


# =========================
# GRAPH EXECUTION
# =========================

async def run_graph(graph, current_state):
    return await graph.ainvoke(current_state)


def print_turn_debug(current_state):
    runs = current_state.get("agent_runs", {})

    print("\n--- ROUTING ---")
    print(json.dumps(current_state.get("routing", {}), indent=2, ensure_ascii=False))
    print("orchestrator run:", runs.get("orchestrator", {}))

    print("\n--- ENERGY ---")
    print("energy_agent run:", runs.get("energy_agent", {}))
    print(json.dumps(current_state.get("energy_decision", {}), indent=2, ensure_ascii=False))

    print("\n--- PROFILE ---")
    print("profile_agent run:", runs.get("profile_agent", {}))
    raw_pv = current_state.get("profile_vector") or {}
    try:
        profile_obj = ProfileInference.model_validate(raw_pv)
        print(ProfileInference.__name__ + " (parsed):")
        print(profile_obj.model_dump_json(indent=2))
    except Exception as e:
        print("profile_vector (parse failed):", e)
        print(json.dumps(raw_pv, indent=2, ensure_ascii=False))

    print("\n--- RAG ---")
    print("rag_agent run:", runs.get("rag_agent", {}))
    print("retrieved_chunks count:", len(current_state.get("retrieved_chunks", [])))

    print("\n--- READINESS OUTPUT ---")
    print("readiness_agent run:", runs.get("readiness_agent", {}))
    print(json.dumps(current_state.get("readiness_signal", {}), indent=2, ensure_ascii=False))

    print("\n--- MERGED SIGNAL BUNDLE ---")
    bundle = current_state.get("merged_signal_bundle") or {}
    slim = {k: v for k, v in bundle.items() if k != "retrieved_chunks"}
    slim["retrieved_chunk_count"] = len(bundle.get("retrieved_chunks") or [])
    print(json.dumps(slim, indent=2, default=str, ensure_ascii=False))

    print("\n--- RESPONSE DRAFT ---")
    print(json.dumps(current_state.get("response_draft", {}), indent=2, ensure_ascii=False))

    print("\n--- ASSISTANT ---\n")
    result = current_state.get("final_response")
    if isinstance(result, list):
        print("Quiz output:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(result)

    print("\n--- LEARNING ---")
    print("learning_agent run:", runs.get("learning_agent", {}))

    print("\n--- SUMMARY ---")
    print(current_state.get("conversation_summary"))

    print("\n--- HISTORY LEN ---")
    print(len(current_state.get("session_history", [])))

    print("\n--- WARNINGS ---")
    print(json.dumps(current_state.get("warnings", []), indent=2, ensure_ascii=False))

    if isinstance(result, str):
        print("\n--- RESPONSE LENGTH ---")
        print(len(result))


def print_planning_debug(current_state):
    runs = current_state.get("agent_runs", {})

    print("\n==============================")
    print("SESSION CLOSED → NEXT STUDY PLAN GENERATED")
    print("==============================")

    print("\n--- PLANNING AGENT ---")
    print("planning_agent run:", runs.get("planning_agent", {}))

    print("\n--- PLANNING TASK ---")
    print(json.dumps(current_state.get("planning_task", {}), indent=2, ensure_ascii=False))

    print("\n--- TODAY SUMMARY ---")
    print(current_state.get("planning_task", {}).get("today_summary"))

    print("\n--- TOMORROW PLAN ---")
    print(json.dumps(
        current_state.get("planning_task", {}).get("tomorrow_plan", []),
        indent=2,
        ensure_ascii=False
    ))


# =========================
# MAIN
# =========================

async def main():
    global state

    print("Starting 2-turn study session test...\n")

    graph = build_learning_graph()
    print("Graph built\n")

    for i, (intent, query) in enumerate(queries):
        print(f"\n👉 Study Turn {i + 1}")

        if i == 1:
            print("Simulating higher fatigue / lighter path")
            state["readiness_signal"]["behavioral_fatigue_band"] = "high"

        print("\n==============================")
        print(f"USER: {query}")
        print(f"INTENT: {intent}")
        print("==============================\n")

        state["query"] = query
        state["routing"] = {"intent": intent}
        state["session_action"] = "continue"
        state["passive_behavior_signals"] = readiness_scenarios[
            min(i, len(readiness_scenarios) - 1)
        ]

        print("\n--- PASSIVE BEHAVIOR (before run) ---")
        print(json.dumps(state.get("passive_behavior_signals", {}), indent=2, ensure_ascii=False))

        try:
            state = await run_graph(graph, state)
        except Exception as e:
            print("ERROR during study graph execution:", str(e))
            break

        print_turn_debug(state)

    # terminal interaction after 2 study turns
    print("\n======================================")
    print("Study session finished for this test.")
    print("Did the user click 'Next study plan'?")
    print("Type 'yes' to stop studying and generate the next plan.")
    print("Type 'no' to keep the session open.")
    print("======================================\n")

    user_choice = input("Your choice (yes/no): ").strip().lower()

    if user_choice == "yes":
        state["session_action"] = "stop"

        # optional marker in history
        state["session_history"].append({
            "role": "user",
            "content": "[SESSION ACTION] stop_studying_and_generate_next_plan"
        })

        # for the planner run, query can be a control message
        state["query"] = "Generate my next study plan for tomorrow."

        try:
            state = await run_graph(graph, state)
        except Exception as e:
            print("ERROR during planning trigger:", str(e))
            return

        print_planning_debug(state)

    else:
        print("\nSession remains open. Planning agent was not triggered.")
        print("Current session_action:", state.get("session_action"))


if __name__ == "__main__":
    asyncio.run(main())