from dotenv import load_dotenv
import os
import json

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from ai.agents.rag.agent import rag_agent
from ai.agents.learning.agent import learning_agent


# INITIAL STATE (persistent)

state = {
    "session_history": [],
    "conversation_summary": "",

    "energy_decision": {"mode": "balanced"},
    "profile_vector": {"preferred_explanation_style": "simple"},
    "readiness_signal": {"behavioral_fatigue_band": "low"},

    "course_context": {},
    "agent_runs": {},
    "errors": []
}



# CONVERSATION TEST

queries = [
    ("learn_concept", "What is a decorator in python?"),
    ("learn_concept", "Can you explain it more simply?"),
    ("practice", "Give me exercises on it"),
    ("revise", "Now help me revise it")
]


for intent, query in queries:

    print("\n==============================")
    print(f"USER: {query}")
    print(f"INTENT: {intent}")
    print("==============================\n")

    # update state
    state["query"] = query
    state["routing"] = {"intent": intent}

    # -------------------------
    # RAG
    # -------------------------
    state = {**state, **rag_agent(state)}

    print("Retrieved Chunks:", len(state.get("retrieved_chunks", [])))

    # -------------------------
    # LEARNING AGENT
    # -------------------------
    state = {**state, **learning_agent(state)}

    result = state.get("final_response")

    print("\nASSISTANT:\n")

    # handle JSON quiz
    if isinstance(result, list):
        print("📚 Quiz Output:\n")
        print(json.dumps(result, indent=2))
    else:
        print(result)

    # -------------------------
    # DEBUG MEMORY
    # -------------------------
    print("\n--- Conversation Summary ---")
    print(state.get("conversation_summary"))

    print("\n--- History Length ---")
    print(len(state.get("session_history", [])))