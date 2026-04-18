import asyncio
import json
import os

from dotenv import load_dotenv

# =========================
# ENV + LANGSMITH
# =========================

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Enable LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "edu-ai-hackathon"

from langsmith import traceable
from ai.graph.learning_workflow import build_learning_graph


# =========================
# INITIAL STATE (PERSISTENT)
# =========================

state = {
    "session_history": [],
    "conversation_summary": "",

    # 🔋 Energy Agent Output (simulated)
    "energy_decision": {
        "mode": "balanced",
        "max_tokens": 400,
        "temperature": 0.3,
        "use_rag": True,
        "top_k": 5,
        "chunk_truncation_chars": 600,
        "generate_quiz": True,
        "include_sources": True,
        "response_depth": "medium"
    },

    # 🧠 Readiness
    "readiness_signal": {
        "behavioral_fatigue_band": "low"
    },

    # 📅 Calendar for planner
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


# =========================
# TEST SCENARIO
# =========================

queries = [
    ("learn_concept", "What is a decorator in python?"),
    ("practice", "Give me exercises on it"),
    ("revise", "Now help me revise it"),
    ("learn_concept", "Explain it deeply with examples"),
]


# =========================
# TRACEABLE EXECUTION
# =========================

@traceable(name="learning_session")
async def run_graph(graph, state):
    return await graph.ainvoke(state)


# =========================
# MAIN LOOP
# =========================

async def main():
    global state

    print("🚀 Starting test...\n")

    graph = build_learning_graph()
    print("✅ Graph built\n")

    for i, (intent, query) in enumerate(queries):

        print(f"\n👉 Turn {i+1}")

        # -------------------------
        # ENERGY MODE SIMULATION
        # -------------------------
        if i == 1:
            print("⚡ Switching to LIGHT mode")
            state["energy_decision"].update({
                "mode": "light",
                "max_tokens": 150,
                "generate_quiz": False,
                "include_sources": False,
                "response_depth": "short",
                "top_k": 3
            })

        elif i == 2:
            print("⚖️ Switching to BALANCED mode")
            state["energy_decision"].update({
                "mode": "balanced",
                "max_tokens": 400,
                "generate_quiz": True,
                "include_sources": True,
                "response_depth": "medium",
                "top_k": 5
            })

        elif i == 3:
            print("🔥 Switching to DEEP mode")
            state["energy_decision"].update({
                "mode": "deep",
                "max_tokens": 700,
                "generate_quiz": True,
                "include_sources": True,
                "response_depth": "long",
                "top_k": 8
            })

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
        # RUN GRAPH
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
        # DEBUG / OBSERVABILITY
        # -------------------------
        print("\n--- ENERGY ---")
        print(json.dumps(state.get("energy_decision", {}), indent=2))

        print("\n--- RAG META ---")
        print(state.get("agent_runs", {}).get("rag_agent", {}))

        print("\n--- LEARNING META ---")
        print(state.get("agent_runs", {}).get("learning_agent", {}))

        print("\n--- PLANNER META ---")
        print(state.get("agent_runs", {}).get("planning_agent", {}))

        print("\n--- SUMMARY ---")
        print(state.get("conversation_summary"))

        print("\n--- HISTORY LEN ---")
        print(len(state.get("session_history", [])))

        print("\n--- PLANNER OUTPUT ---")
        planning = state.get("planning_task")
        if planning:
            print(json.dumps(planning, indent=2))
        else:
            print("No plan generated")

        if isinstance(result, str):
            print("\n--- RESPONSE LENGTH ---")
            print(len(result))


# =========================
# ENTRY POINT
# =========================

if __name__ == "__main__":
    asyncio.run(main())