from typing import Dict


def energy_agent(state: dict) -> dict:
    """
    Decides how much compute to use (energy-aware inference).
    """

    query = state.get("query", "")
    intent = state.get("routing", {}).get("intent", "learn_concept")
    readiness = state.get("readiness_signal", {})
  
    # Heuristics
 

    query_length = len(query.split())
    fatigue = readiness.get("behavioral_fatigue_band", "low")

  
    # Decide mode

    if fatigue == "high":
        mode = "light"
    elif intent == "practice":
        mode = "balanced"
    elif query_length > 20:
        mode = "deep"
    else:
        mode = "balanced"

    # Map mode → behavior

    if mode == "light":
        decision = {
            "mode": "light",
            "max_tokens": 200,
            "use_rag": True,
            "use_profile": False,
            "use_readiness": True,
            "response_depth": "short",
            "reason": "User fatigue high → reduce compute and simplify response"
        }

    elif mode == "deep":
        decision = {
            "mode": "deep",
            "max_tokens": 800,
            "use_rag": True,
            "use_profile": True,
            "use_readiness": True,
            "response_depth": "long",
            "reason": "Complex query → allow deeper reasoning"
        }

    else:  # balanced
        decision = {
            "mode": "balanced",
            "max_tokens": 400,
            "use_rag": True,
            "use_profile": True,
            "use_readiness": False,
            "response_depth": "medium",
            "reason": "Standard response"
        }

    return {
        "energy_decision": decision,
        "agent_runs": {
            **state.get("agent_runs", {}),
            "energy_agent": {
                "status": "success"
            }
        }
    }