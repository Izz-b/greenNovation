from __future__ import annotations

from typing import Literal

IntentType = Literal[
    "learn_concept",
    "practice",
    "revise",
    "plan_study",
    "wellbeing_check",
    "mixed",
    "unknown",
]


def classify_intent(query: str) -> tuple[IntentType, str]:
    q = (query or "").strip().lower()

    has_practice = any(k in q for k in ["exercise", "exercises", "practice", "quiz", "problems"])
    has_revision = any(k in q for k in ["revise", "revision", "review", "summary", "summarize"])
    has_planning = any(k in q for k in ["study plan", "schedule", "roadmap", "organize my study"])
    has_wellbeing = any(k in q for k in ["stressed", "overwhelmed", "burnout", "anxious", "tired"])
    has_learning = any(k in q for k in ["explain", "teach me", "what is", "help me understand"])

    matched = sum([has_practice, has_revision, has_planning, has_wellbeing, has_learning])

    if matched > 1:
        return "mixed", "Multiple intent patterns detected."
    if has_practice:
        return "practice", "Practice-oriented wording detected."
    if has_revision:
        return "revise", "Revision-oriented wording detected."
    if has_planning:
        return "plan_study", "Planning-oriented wording detected."
    if has_wellbeing:
        return "wellbeing_check", "Wellbeing-related wording detected."
    if has_learning:
        return "learn_concept", "Concept-learning wording detected."

    return "unknown", "No strong intent detected."


def select_agents(intent: IntentType) -> list[str]:
    if intent == "learn_concept":
        return ["profile", "rag", "readiness", "energy"]
    if intent == "practice":
        return ["profile", "rag", "readiness", "energy"]
    if intent == "revise":
        return ["profile", "rag", "readiness", "energy"]
    if intent == "plan_study":
        return ["profile", "readiness", "energy"]
    if intent == "wellbeing_check":
        return ["profile", "readiness", "energy"]
    if intent == "mixed":
        return ["profile", "rag", "readiness", "energy"]
    return ["profile", "energy"]


def build_routing(intent: IntentType, route_reason: str) -> dict:
    requested_agents = select_agents(intent)

    priority = "normal"
    if intent in {"mixed", "wellbeing_check"}:
        priority = "high"

    token_budget = 2500
    if intent in {"practice", "revise", "mixed"}:
        token_budget = 3200
    elif intent == "wellbeing_check":
        token_budget = 1800

    return {
        "intent": intent,
        "requested_agents": requested_agents,
        "route_reason": route_reason,
        "priority": priority,
        "token_budget": token_budget,
    }