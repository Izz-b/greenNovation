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
}



# TEST SCENARIO


queries = [
    ("learn_concept", "What is a decorator in python?"),
    ("practice", "Give me exercises on it"),
    ("revise", "Now help me revise it"),
    ("learn_concept", "Explain it deeply with examples"),
]



# TRACEABLE EXECUTION


@traceable(name="learning_session")
async def run_graph(graph, state):
    return await graph.ainvoke(state)


# MAIN LOOP


async def main():
    global state

    print("🚀 Starting test...\n")

    graph = build_learning_graph()
    print("✅ Graph built\n")

    for i, (intent, query) in enumerate(queries):

        print(f"\n👉 Turn {i+1}")

        # -------------------------
        # SIMULATE FATIGUE (for energy agent)
        # -------------------------
        if i == 1:
            print("⚡ Simulating HIGH fatigue → should trigger LIGHT mode")
            state["readiness_signal"]["behavioral_fatigue_band"] = "high"

        elif i == 2:
            print("⚖️ Simulating LOW fatigue → balanced mode")
            state["readiness_signal"]["behavioral_fatigue_band"] = "low"

        elif i == 3:
            print("🔥 Long query → should trigger DEEP mode")

        # -------------------------
        # USER INPUT
        # -------------------------
        print("\n==============================")
        print(f"USER: {query}")
        print(f"INTENT: {intent}")
        print("==============================\n")

        state["query"] = query
        state["routing"] = {"intent": intent}

        # -------------------------
        # RUN GRAPH (ONLY ONCE)
        # -------------------------
        try:
            state = await run_graph(graph, state)
        except Exception as e:
            print("❌ ERROR during graph execution:", str(e))
            break

        result = state.get("final_response")

        # -------------------------
        # OUTPUT
        # -------------------------
        print("\nASSISTANT:\n")

        if isinstance(result, list):
            print("📚 Quiz Output:\n")
            print(json.dumps(result, indent=2))
        else:
            print(result)

        # -------------------------
        # PROFILE DEBUG
        # -------------------------
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
        print("\n--- SUMMARY ---")
        print(state.get("conversation_summary"))

        print("\n--- HISTORY LEN ---")
        print(len(state.get("session_history", [])))

        # -------------------------
        # RESPONSE LENGTH
        # -------------------------
        if isinstance(result, str):
            print("\n--- RESPONSE LENGTH ---")
            print(len(result))



# ENTRY POINT


if __name__ == "__main__":
    asyncio.run(main())