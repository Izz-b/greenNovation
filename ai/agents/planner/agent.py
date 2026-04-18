from typing import Dict, List, Any
from langchain_groq import ChatGroq
import json

# LLM

def get_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.2  # more deterministic
    )



# HISTORY BUILDER


def build_history(session_history: List[Dict], max_turns: int = 6) -> str:
    history = ""
    for turn in session_history[-max_turns:]:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        prefix = "User" if role == "user" else "Assistant"
        history += f"{prefix}: {content}\n"
    return history


# PROMPT BUILDER


def build_planner_prompt(state: dict) -> str:

    summary = state.get("conversation_summary", "")
    history = build_history(state.get("session_history", []))

    energy = state.get("energy_decision", {})
    readiness = state.get("readiness_signal", {})
    calendar = state.get("planning_task", {}).get("calendar", {})

    fatigue = readiness.get("behavioral_fatigue_band", "low")
    mode = energy.get("mode", "balanced")

    return f"""
You are an academic planning assistant.

Your role:
- Summarize what the student learned today
- Plan the next study session (tomorrow)

You MUST adapt to:
- Energy mode: {mode}
- Fatigue level: {fatigue}

Rules:
- If fatigue is high → reduce workload
- If energy mode is light → short session
- If deep → allow longer + harder tasks

Return ONLY valid JSON:

{{
  "today_summary": "...",
  "tomorrow_plan": [
    {{
      "task": "...",
      "duration_minutes": 20,
      "priority": "high|medium|low"
    }}
  ],
  "recommended_duration": 30,
  "intensity": "light|balanced|deep"
}}

CONTEXT:

Conversation Summary:
{summary}

Recent History:
{history}

Calendar:
{calendar}
"""
    


# OUTPUT PARSER

def parse_planner_output(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except:
        return {
            "today_summary": "Could not parse summary",
            "tomorrow_plan": [],
            "recommended_duration": 20,
            "intensity": "light"
        }


# PLANNER AGENT NODE

def planning_agent(state: dict) -> dict:
    """
    Creates study plan based on learning + energy + calendar.
    """

    try:
        llm = get_llm()

        prompt = build_planner_prompt(state)

        response = llm.invoke(prompt)
        raw_output = response.content.strip()

        parsed = parse_planner_output(raw_output)

        return {
            "planning_task": parsed,

            "agent_runs": {
                **state.get("agent_runs", {}),
                "planning_agent": {
                    "status": "success"
                }
            }
        }

    except Exception as e:
        return {
            "planning_task": {},
            "errors": state.get("errors", []) + [f"planning_agent error: {str(e)}"],
            "agent_runs": {
                **state.get("agent_runs", {}),
                "planning_agent": {
                    "status": "failed",
                    "error": str(e)
                }
            }
        }