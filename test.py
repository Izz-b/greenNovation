from dotenv import load_dotenv
import os
import json

# Load env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from ai.agents.rag.agent import rag_agent
from ai.agents.learning.agent import learning_agent



# TEST CASES


test_cases = [
    ("learn_concept", "Explain what is a decorator in python"),
    ("practice", "Give me exercises on python decorators"),
    ("revise", "Help me revise decorators"),
    ("mixed", "Explain decorators and give practice questions")
]


for intent, query in test_cases:

    print("\n==============================")
    print(f"TESTING INTENT: {intent}")
    print("==============================\n")

    # INITIAL STATE
    state = {
        "query": query,

        "routing": {
            "intent": intent
        },

        "energy_decision": {
            "mode": "balanced",  # try: light / deep
        },

        "profile_vector": {
            "preferred_explanation_style": "simple"
        },

        "readiness_signal": {
            "behavioral_fatigue_band": "low"
        },

        "course_context": {},
        "agent_runs": {},
        "errors": []
    }

   
    # RAG
   
    state = {**state, **rag_agent(state)}

    print("\n--- Retrieved Chunks ---")
    print(len(state.get("retrieved_chunks", [])))

  
    # LEARNING AGENT
    
    state = {**state, **learning_agent(state)}

    result = state.get("final_response")

    print("\n--- Final Output ---\n")

   
    # HANDLE OUTPUT TYPES
  
    if isinstance(result, list):
        print("📚 Quiz Output (JSON):\n")
        print(json.dumps(result, indent=2))
    else:
        print(result)

    print("\n--- Agent Status ---")
    print(state.get("agent_runs"))