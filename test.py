from dotenv import load_dotenv
import os

# Load env (important for Groq)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from ai.rag.agent import rag_agent
from ai.learning.agent import learning_agent


# =========================
# INITIAL STATE (simulate user input)
# =========================

state = {
    "query": "Explain what is a decorator in python",

    # optional but useful for your adaptive system
    "energy_decision": {
        "response_depth": "medium"
    },
    "profile_vector": {
        "preferred_explanation_style": "simple"
    },
    "readiness_signal": {
        "behavioral_fatigue_band": "low"
    },

    "course_context": {},  # or add filters if you use them
    "agent_runs": {},
    "errors": []
}


# =========================
# RUN RAG AGENT
# =========================

state = {**state, **rag_agent(state)}

print("\n--- Retrieved Chunks ---")
print(len(state.get("retrieved_chunks", [])))


# =========================
# RUN LEARNING AGENT
# =========================

state = {**state, **learning_agent(state)}

print("\n--- Final Answer ---\n")
print(state.get("final_response"))