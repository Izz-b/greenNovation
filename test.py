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
    # energy_decision is set in orchestrator before profile/RAG/readiness
    # readiness_signal: seed band for simulation; overwritten if readiness runs
    "readiness_signal": {
        "behavioral_fatigue_band": "low"
    },
    # Calendar (for planner later)
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


# TRACEABLE EXECUTION


@traceable(name="learning_session")
async def run_graph(graph, state):
    return await graph.ainvoke(state)


# MAIN LOOP


async def main():
    global state

    print("Starting orchestrated test...\n")

    graph = build_learning_graph()
    print("Graph built\n")

    for i, (intent, query) in enumerate(queries):
        print(f"\n👉 Turn {i + 1}")

        # SIMULATE FATIGUE (for energy agent)
        if i == 1:
            print("Simulating HIGH fatigue (LIGHT mode path)")
            state["readiness_signal"]["behavioral_fatigue_band"] = "high"

        elif i == 2:
            print("Simulating LOW fatigue (balanced path)")
            state["readiness_signal"]["behavioral_fatigue_band"] = "low"

        elif i == 3:
            print("Long query (DEEP mode path)")

        print("\n==============================")
        print(f"USER: {query}")
        print(f"INTENT: {intent}")
        print("==============================\n")

        state["query"] = query
        state["routing"] = {"intent": intent}
        state["passive_behavior_signals"] = readiness_scenarios[
            min(i, len(readiness_scenarios) - 1)
        ]

        print("\n--- PASSIVE BEHAVIOR (readiness input, before run) ---")
        print(json.dumps(state.get("passive_behavior_signals", {}), indent=2))

        try:
            state = await run_graph(graph, state)
        except Exception as e:
            print("ERROR during graph execution:", str(e))
            raw_pv = state.get("profile_vector") or {}
            print("Profile vector at failure (if any):")
            print(json.dumps(raw_pv, indent=2, ensure_ascii=False))
            break

        runs = state.get("agent_runs", {})
        # Same order as inside orchestrator_agent: routing → energy → profile →
        # RAG → readiness → merge, then the graph runs learning on top.
        print("\n--- ROUTING (orchestrator) ---")
        print(json.dumps(state.get("routing", {}), indent=2))
        print("orchestrator run:", runs.get("orchestrator", {}))

        print("\n--- ENERGY (1st in pipeline) ---")
        print("energy_agent run:", runs.get("energy_agent", {}))
        print(json.dumps(state.get("energy_decision", {}), indent=2, ensure_ascii=False))

        print("\n--- PROFILE ---")
        print("profile_agent run:", runs.get("profile_agent", {}))
        raw_pv = state.get("profile_vector") or {}
        try:
            profile_obj = ProfileInference.model_validate(raw_pv)
            print(ProfileInference.__name__ + " (parsed):")
            print(profile_obj.model_dump_json(indent=2))
        except Exception as e:
            print("profile_vector (parse failed):", e)
            print(json.dumps(raw_pv, indent=2, ensure_ascii=False))

        print("\n--- RAG ---")
        print("rag_agent run:", runs.get("rag_agent", {}))
        print("retrieved_chunks count:", len(state.get("retrieved_chunks", [])))

        print("\n--- READINESS OUTPUT (readiness agent) ---")
        print("readiness_agent run:", runs.get("readiness_agent", {}))
        print(json.dumps(state.get("readiness_signal", {}), indent=2, ensure_ascii=False))

        print("\n--- MERGED SIGNAL BUNDLE (orchestrator merge) ---")
        bundle = state.get("merged_signal_bundle") or {}
        slim = {k: v for k, v in bundle.items() if k != "retrieved_chunks"}
        slim["retrieved_chunk_count"] = len(bundle.get("retrieved_chunks") or [])
        print(json.dumps(slim, indent=2, default=str, ensure_ascii=False))

        print("\n--- RESPONSE DRAFT ---")
        print(json.dumps(state.get("response_draft", {}), indent=2, ensure_ascii=False))

        print("\n--- ASSISTANT (learning) ---\n")
        result = state.get("final_response")
        if isinstance(result, list):
            print("Quiz output:")
            print(json.dumps(result, indent=2))
        else:
            print(result)

        print("\n--- LEARNING (graph node) ---")
        print("learning_agent run:", runs.get("learning_agent", {}))

        print("\n--- SUMMARY ---")
        print(state.get("conversation_summary"))

        print("\n--- HISTORY LEN ---")
        print(len(state.get("session_history", [])))

        print("\n--- WARNINGS ---")
        print(json.dumps(state.get("warnings", []), indent=2, ensure_ascii=False))

        if isinstance(result, str):
            print("\n--- RESPONSE LENGTH ---")
            print(len(result))


if __name__ == "__main__":
    asyncio.run(main())
