from __future__ import annotations

from typing import Any, Dict, List

from ai.state.agent_context import MessageTurn, UserProfile


def _normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def _recent_user_text(session_history: List[MessageTurn], limit: int = 6) -> str:
    messages = [
        turn.get("content", "")
        for turn in session_history[-limit:]
        if turn.get("role") == "user"
    ]
    return " ".join(messages).lower()


def _detect_topic_domain(query: str, user_profile: UserProfile) -> str:
    q = _normalize_text(query)
    department = _normalize_text(user_profile.get("department", ""))

    if any(k in q for k in ["python", "algorithm", "database", "sql", "code", "recursion"]):
        return "computer_science"
    if any(k in q for k in ["math", "calculus", "algebra", "probability", "derivative"]):
        return "mathematics"
    if any(k in q for k in ["network", "signal", "telecom", "communication"]):
        return "engineering"

    if "software" in department or "computer" in department:
        return "computer_science"
    if "telecom" in department or "engineering" in department:
        return "engineering"

    return "general"


def build_profile_features(
    query: str,
    session_history: List[MessageTurn],
    user_profile: UserProfile,
) -> Dict[str, Any]:
    query_text = _normalize_text(query)
    history_text = _recent_user_text(session_history)
    combined = f"{query_text} {history_text}"

    asked_for_examples_count = (
        combined.count("example")
        + combined.count("examples")
        + combined.count("real world")
    )

    asked_for_simplification_count = (
        combined.count("simple")
        + combined.count("simplify")
        + combined.count("easy")
        + combined.count("step by step")
        + combined.count("one by one")
    )

    prefers_short_answers = any(
        k in combined for k in ["short", "brief", "quick", "concise"]
    )

    prefers_detailed_answers = any(
        k in combined for k in ["detailed", "deep", "more detail", "in depth"]
    )

    exam_related = any(
        k in combined for k in ["exam", "revision", "review", "quiz", "test"]
    )

    practice_related = any(
        k in combined for k in ["exercise", "practice", "problems", "quiz"]
    )

    signs_of_confusion = any(
        k in combined for k in [
            "i don't understand",
            "i dont understand",
            "confused",
            "lost",
            "hard for me",
            "i struggle",
        ]
    )

    topic_domain = _detect_topic_domain(query, user_profile)

    return {
        "asked_for_examples_count": asked_for_examples_count,
        "asked_for_simplification_count": asked_for_simplification_count,
        "prefers_short_answers": prefers_short_answers,
        "prefers_detailed_answers": prefers_detailed_answers,
        "exam_related": exam_related,
        "practice_related": practice_related,
        "signs_of_confusion": signs_of_confusion,
        "topic_domain": topic_domain,
        "department": user_profile.get("department", ""),
        "academic_level": user_profile.get("academic_level", ""),
        "learning_style_explicit": user_profile.get("learning_style", ""),
        "pace_preference_explicit": user_profile.get("pace_preference", ""),
        "accessibility_needs": user_profile.get("accessibility_needs", []),
    }