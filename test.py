import asyncio
import json
import os

from dotenv import load_dotenv


# ENV + LANGSMITH


load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Enable LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "edu-ai-hackathon"

from langsmith import traceable
from ai.agents.profile.schema import ProfileInference
from ai.graph.learning_workflow import build_learning_graph



# INITIAL STATE (PERSISTENT)

state = {
    "session_history": [],
    "conversation_summary": "",
    # energy_decision is set each turn by energy_agent (after readiness)

  

    # 🧠 Readiness (used by energy agent)
    "readiness_signal": {
        "behavioral_fatigue_band": "low"
    },

    # 📅 Calendar (for planner later)
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



# TEST SCENARIO


queries = [
    ("learn_concept", "What is a decorator in python?"),
    ("practice", "Give me exercises on it"),
    ("revise", "Now help me revise it"),
<<<<<<< HEAD
    ("learn_concept", "Explain it deeply with examples"),
]


async def main():
    global state

    print("🚀 Starting orchestrated test...\n")
=======
<<<<<<< HEAD
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
=======
    ("learn_concept", "Explain it deeply with examples"),
>>>>>>> f6810fd72b1e0d5019d02d47bdc888fc57277223
]



# TRACEABLE EXECUTION


@traceable(name="learning_session")
async def run_graph(graph, state):
    return await graph.ainvoke(state)


# MAIN LOOP


async def main():
    global state

    print("Starting test...\n")
>>>>>>> 8cd14d90e75c22fc889fe5928dbbf80aebf7ce1e

    graph = build_learning_graph()
    print("Graph built\n")

    for i, (intent, query) in enumerate(queries):
<<<<<<< HEAD
        print(f"\n👉 Turn {i+1}")

=======

<<<<<<< HEAD
        print(f"\nTurn {i+1}")
=======
        print(f"\n👉 Turn {i+1}")

        # -------------------------
        # SIMULATE FATIGUE (for energy agent)
        # -------------------------
>>>>>>> 8cd14d90e75c22fc889fe5928dbbf80aebf7ce1e
        if i == 1:
            print("⚡ Simulating HIGH fatigue → should trigger LIGHT mode")
            state["readiness_signal"]["behavioral_fatigue_band"] = "high"

        elif i == 2:
            print("⚖️ Simulating LOW fatigue → balanced mode")
            state["readiness_signal"]["behavioral_fatigue_band"] = "low"

        elif i == 3:
            print("🔥 Long query → should trigger DEEP mode")
>>>>>>> f6810fd72b1e0d5019d02d47bdc888fc57277223

        print("\n==============================")
        print(f"USER: {query}")
        print(f"INTENT: {intent}")
        print("==============================\n")

        state["query"] = query
        state["routing"] = {"intent": intent}
        state["passive_behavior_signals"] = readiness_scenarios[min(i, len(readiness_scenarios) - 1)]

<<<<<<< HEAD
        state = await graph.ainvoke(state)

        print("Orchestrator:", state.get("agent_runs", {}).get("orchestrator", {}))
        print("Profile agent:", state.get("agent_runs", {}).get("profile_agent", {}))
        print("RAG agent:", state.get("agent_runs", {}).get("rag_agent", {}))
        print("Readiness agent:", state.get("agent_runs", {}).get("readiness_agent", {}))
        print("Energy agent:", state.get("agent_runs", {}).get("energy_agent", {}))
        print("Learning agent:", state.get("agent_runs", {}).get("learning_agent", {}))

        raw_pv = state.get("profile_vector") or {}
=======
        # -------------------------
        # RUN GRAPH (ONLY ONCE)
        # -------------------------
>>>>>>> 8cd14d90e75c22fc889fe5928dbbf80aebf7ce1e
        try:
            state = await run_graph(graph, state)
        except Exception as e:
<<<<<<< HEAD
            print("\n--- ProfileInference (raw dict; validate failed) ---", e)
            print(json.dumps(raw_pv, indent=2, ensure_ascii=False))
=======
            print("❌ ERROR during graph execution:", str(e))
            break
>>>>>>> 8cd14d90e75c22fc889fe5928dbbf80aebf7ce1e

        print("\n--- ROUTING ---")
        print(json.dumps(state.get("routing", {}), indent=2))

        print("\n--- MERGED SIGNAL BUNDLE ---")
        print(json.dumps(state.get("merged_signal_bundle", {}), indent=2, ensure_ascii=False))

        print("\n--- RESPONSE DRAFT ---")
        print(json.dumps(state.get("response_draft", {}), indent=2, ensure_ascii=False))

        print("\nASSISTANT:\n")
        result = state.get("final_response")
        if isinstance(result, list):
<<<<<<< HEAD
=======
            print("Quiz Output:\n")
>>>>>>> 8cd14d90e75c22fc889fe5928dbbf80aebf7ce1e
            print(json.dumps(result, indent=2))
        else:
            print(result)

<<<<<<< HEAD
        print("\n--- ENERGY ---")
        print(json.dumps(state.get("energy_decision", {}), indent=2))

=======
        # -------------------------
        # PROFILE DEBUG
        # -------------------------
<<<<<<< HEAD
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

=======
        print("\n--- PROFILE ---")
        print(state.get("agent_runs", {}).get("profile_agent", {}))

        raw_pv = state.get("profile_vector") or {}
        try:
            profile_obj = ProfileInference.model_validate(raw_pv)
            print("\n--- ProfileInference ---")
            print(profile_obj.model_dump_json(indent=2))
        except Exception as e:
            print("\n--- ProfileInference (raw dict) ---", e)
            print(json.dumps(raw_pv, indent=2, ensure_ascii=False))

        # -------------------------
        # ENERGY DEBUG (KEY PART)
        # -------------------------
        print("\n--- ENERGY DECISION ---")
        print(json.dumps(state.get("energy_decision", {}), indent=2))

        print("\n--- ENERGY META ---")
        print(state.get("agent_runs", {}).get("energy_agent", {}))

        # -------------------------
        # RAG DEBUG
        # -------------------------
>>>>>>> f6810fd72b1e0d5019d02d47bdc888fc57277223
        print("\n--- RAG META ---")
        print(state.get("agent_runs", {}).get("rag_agent", {}))
        print("Retrieved Chunks:", len(state.get("retrieved_chunks", [])))

        # -------------------------
        # LEARNING DEBUG
        # -------------------------
        print("\n--- LEARNING META ---")
        print(state.get("agent_runs", {}).get("learning_agent", {}))

        # -------------------------
        # SUMMARY + MEMORY
        # -------------------------
>>>>>>> 8cd14d90e75c22fc889fe5928dbbf80aebf7ce1e
        print("\n--- SUMMARY ---")
        print(state.get("conversation_summary"))

        print("\n--- HISTORY LEN ---")
        print(len(state.get("session_history", [])))

<<<<<<< HEAD
        print("\n--- WARNINGS ---")
        print(json.dumps(state.get("warnings", []), indent=2, ensure_ascii=False))

=======
        # -------------------------
        # RESPONSE LENGTH
        # -------------------------
>>>>>>> 8cd14d90e75c22fc889fe5928dbbf80aebf7ce1e
        if isinstance(result, str):
            print("\n--- RESPONSE LENGTH ---")
            print(len(result))


<<<<<<< HEAD
=======

# ENTRY POINT


>>>>>>> 8cd14d90e75c22fc889fe5928dbbf80aebf7ce1e
if __name__ == "__main__":
    asyncio.run(main())