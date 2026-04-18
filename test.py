import asyncio
import json
import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from ai.agents.profile.schema import ProfileInference
from ai.graph.learning_workflow import build_learning_graph


# INITIAL STATE (persistent)

state = {
    "session_history": [],
    "conversation_summary": "",

    "energy_decision": {"mode": "balanced"},
    "readiness_signal": {"behavioral_fatigue_band": "low"},

    "course_context": {},
    "agent_runs": {},
    "errors": [],
    "traces": [],
}


# CONVERSATION TEST

queries = [
    ("learn_concept", "What is a decorator in python?"),
    ("learn_concept", "Can you explain it more simply?"),
    ("practice", "Give me exercises on it"),
    ("revise", "Now help me revise it"),
]


async def main():
    global state
    graph = build_learning_graph()

    for intent, query in queries:
        print("\n==============================")
        print(f"USER: {query}")
        print(f"INTENT: {intent}")
        print("==============================\n")

        state["query"] = query
        state["routing"] = {"intent": intent}

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

        print("\nASSISTANT:\n")

        if isinstance(result, list):
            print("📚 Quiz Output:\n")
            print(json.dumps(result, indent=2))
        else:
            print(result)

        print("\n--- Conversation Summary ---")
        print(state.get("conversation_summary"))

        print("\n--- History Length ---")
        print(len(state.get("session_history", [])))


if __name__ == "__main__":
    asyncio.run(main())
