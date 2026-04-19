from typing import Dict, List, Any
from langchain_groq import ChatGroq
import json
from datetime import datetime

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
    calendar = state.get("calendar_events", [])

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
    



def should_run_planner(state: dict) -> bool:
    """
    Run planner only:
    - Once per day
    - OR when explicitly forced (for testing)
    """

    today = datetime.utcnow().date()

    planner_state = state.get("planner_state", {})
    last_date = planner_state.get("last_generated_date")

    # 🧪 Allow manual override (for testing)
    if state.get("force_planner", False):
        return True

    # First time ever → run
    if last_date is None:
        return True

    last_date = datetime.fromisoformat(last_date).date()

    # Run only if new day
    return today > last_date

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
    Runs once per day AFTER meaningful learning.
    """

    try:
        meta = state.get("planner_meta", {
            "last_generated_date": None,
            "turns_since_last_plan": 0
        })

        # Increment turns
        meta["turns_since_last_plan"] = meta.get("turns_since_last_plan", 0) + 1

        # Decide if planner should run
        if not should_run_planner({**state, "planner_meta": meta}):
            return {
                "planner_meta": meta,
                "agent_runs": {
                    **state.get("agent_runs", {}),
                    "planning_agent": {
                        "status": "skipped",
                        "reason": "Not end of session or already generated today"
                    }
                }
            }

        # ✅ RUN PLANNER
        llm = get_llm()
        prompt = build_planner_prompt(state)

        response = llm.invoke(prompt)
        raw_output = response.content.strip()

        parsed = parse_planner_output(raw_output)

        # Update meta
        meta["last_generated_date"] = datetime.now().date().isoformat()
        meta["turns_since_last_plan"] = 0

        return {
            "planning_task": parsed,
            "planner_meta": meta,

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