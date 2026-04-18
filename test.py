import asyncio
import json
import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from ai.agents.profile.schema import ProfileInference
from ai.graph.learning_workflow import build_learning_graph


state = {
    "session_history": [],
    "conversation_summary": "",

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

    "readiness_signal": {"behavioral_fatigue_band": "low"},

    "course_context": {},
    "agent_runs": {},
    "errors": [],
    "traces": [],
    "warnings": [],
}


queries = [
    ("learn_concept", "What is a decorator in python?"),
    ("practice", "Give me exercises on it"),
    ("revise", "Now help me revise it"),
    ("learn_concept", "Explain it deeply with examples"),
]


async def main():
    global state

    print("🚀 Starting orchestrated test...\n")

    graph = build_learning_graph()
    print("✅ Graph built\n")

    for i, (intent, query) in enumerate(queries):
        print(f"\n👉 Turn {i+1}")

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

        print("\n==============================")
        print(f"USER: {query}")
        print(f"INTENT: {intent}")
        print("==============================\n")

        state["query"] = query
        state["routing"] = {"intent": intent}

        state = await graph.ainvoke(state)

        print("Orchestrator:", state.get("agent_runs", {}).get("orchestrator", {}))
        print("Profile agent:", state.get("agent_runs", {}).get("profile_agent", {}))
        print("RAG agent:", state.get("agent_runs", {}).get("rag_agent", {}))
        print("Readiness agent:", state.get("agent_runs", {}).get("readiness_agent", {}))
        print("Energy agent:", state.get("agent_runs", {}).get("energy_agent", {}))
        print("Learning agent:", state.get("agent_runs", {}).get("learning_agent", {}))

        raw_pv = state.get("profile_vector") or {}
        try:
            profile_obj = ProfileInference.model_validate(raw_pv)
            print("\n--- ProfileInference ---")
            print(profile_obj.model_dump_json(indent=2))
        except Exception as e:
            print("\n--- ProfileInference (raw dict; validate failed) ---", e)
            print(json.dumps(raw_pv, indent=2, ensure_ascii=False))

        print("\n--- ROUTING ---")
        print(json.dumps(state.get("routing", {}), indent=2))

        print("\n--- MERGED SIGNAL BUNDLE ---")
        print(json.dumps(state.get("merged_signal_bundle", {}), indent=2, ensure_ascii=False))

        print("\n--- RESPONSE DRAFT ---")
        print(json.dumps(state.get("response_draft", {}), indent=2, ensure_ascii=False))

        print("\nASSISTANT:\n")
        result = state.get("final_response")
        if isinstance(result, list):
            print(json.dumps(result, indent=2))
        else:
            print(result)

        print("\n--- ENERGY ---")
        print(json.dumps(state.get("energy_decision", {}), indent=2))

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