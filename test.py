import asyncio
import json
import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from ai.agents.profile.schema import ProfileInference
from ai.graph.learning_workflow import build_learning_graph


# =========================
# INITIAL STATE (persistent)
# =========================

state = {
    "session_history": [],
    "conversation_summary": "",
    # energy_decision is set each turn by energy_agent (after readiness)

    "passive_behavior_signals": {
        "tasks_due_3d": 2,
        "overdue_tasks": 0,
        "project_risk_level": "low",
        "study_sessions_last_7d": 5,
        "avg_session_completion_rate": 0.8,
        "avg_quiz_score_trend": 4.0,
        "late_night_activity_ratio": 0.1,
        "long_sessions_without_breaks": 0,
    },

    "course_context": {},
    "agent_runs": {},
    "errors": [],
    "traces": [],
}


# =========================
# CONVERSATION TEST
# =========================

queries = [
    ("learn_concept", "What is a decorator in python?"),
    ("practice", "Give me exercises on it"),
    ("revise", "Now help me revise it"),
    ("learn_concept", "Explain it deeply with examples"),  # deep case
]

readiness_scenarios = [
    # Turn 1: healthy baseline
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
    # Turn 2: rising pressure/fatigue
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
    # Turn 3: highest pressure
    {
        "tasks_due_3d": 7,
        "overdue_tasks": 2,
        "project_risk_level": "high",
        "study_sessions_last_7d": 2,
        "avg_session_completion_rate": 0.5,
        "avg_quiz_score_trend": -8.0,
        "late_night_activity_ratio": 0.55,
        "long_sessions_without_breaks": 3,
    },
    # Turn 4: recovery
    {
        "tasks_due_3d": 3,
        "overdue_tasks": 0,
        "project_risk_level": "low",
        "study_sessions_last_7d": 4,
        "avg_session_completion_rate": 0.75,
        "avg_quiz_score_trend": 2.0,
        "late_night_activity_ratio": 0.2,
        "long_sessions_without_breaks": 1,
    },
]


# =========================
# MAIN
# =========================

async def main():
    global state

    print("Starting test...\n")

    graph = build_learning_graph()
    print("Graph built\n")

    for i, (intent, query) in enumerate(queries):

        print(f"\nTurn {i+1}")

        # -------------------------
        # USER INPUT
        # -------------------------
        print("\n==============================")
        print(f"USER: {query}")
        print(f"INTENT: {intent}")
        print("==============================\n")

        state["query"] = query
        state["routing"] = {"intent": intent}
        state["passive_behavior_signals"] = readiness_scenarios[min(i, len(readiness_scenarios) - 1)]

        state = await graph.ainvoke(state)

        print("Profile agent:", state.get("agent_runs", {}).get("profile_agent", {}))
        raw_pv = state.get("profile_vector") or {}
        try:
            profile_obj = ProfileInference.model_validate(raw_pv)
            print("\n--- ProfileInference ---")
            print(profile_obj.model_dump_json(indent=2))
        except Exception as e:
            print("\n--- ProfileInference (raw dict; validate failed) ---", e)
            print(json.dumps(raw_pv, indent=2, ensure_ascii=False))
        print("Retrieved Chunks:", len(state.get("retrieved_chunks", [])))

        result = state.get("final_response")

        # -------------------------
        # OUTPUT
        # -------------------------
        print("\nASSISTANT:\n")

        if isinstance(result, list):
            print("Quiz Output:\n")
            print(json.dumps(result, indent=2))
        else:
            print(result)

        # -------------------------
        # DEBUG INFO
        # -------------------------
        print("\n--- PASSIVE BEHAVIOR (readiness input) ---")
        print(json.dumps(state.get("passive_behavior_signals", {}), indent=2))

        print("\n--- ENERGY (from energy_agent) ---")
        print(json.dumps(state.get("energy_decision", {}), indent=2))

        print("\n--- READINESS SIGNAL ---")
        print(json.dumps(state.get("readiness_signal", {}), indent=2))

        print("\n--- MERGED SIGNAL BUNDLE ---")
        bundle = state.get("merged_signal_bundle") or {}
        # Avoid dumping full chunk bodies
        slim = {k: v for k, v in bundle.items() if k != "retrieved_chunks"}
        slim["retrieved_chunk_count"] = len(bundle.get("retrieved_chunks") or [])
        print(json.dumps(slim, indent=2, default=str))

        print("\n--- RAG META ---")
        print(state.get("agent_runs", {}).get("rag_agent", {}))

        print("\n--- LEARNING META ---")
        print(state.get("agent_runs", {}).get("learning_agent", {}))

        print("\n--- SUMMARY ---")
        print(state.get("conversation_summary"))

        print("\n--- HISTORY LEN ---")
        print(len(state.get("session_history", [])))

        if isinstance(result, str):
            print("\n--- RESPONSE LENGTH ---")
            print(len(result))


# =========================
# ENTRY POINT
# =========================

if __name__ == "__main__":
    asyncio.run(main())