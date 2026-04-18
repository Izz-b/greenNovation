from typing import Dict, List, Any
from langchain_groq import ChatGroq
import json


# LLM


def get_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.3
    )


# Context Builder


MAX_CHARS = 800

def build_context(chunks: List[Dict]) -> str:
    context = ""

    for i, c in enumerate(chunks):
        source = c.get("source_id", "unknown")
        page = c.get("metadata", {}).get("page", "?")
        content = c.get("content", "")[:MAX_CHARS]

        context += f"[{i+1}] ({source}, p.{page})\n{content}\n\n"

    return context



# History Builder


def build_history(session_history: List[Dict], max_turns: int = 5) -> str:
    history = ""
    for turn in session_history[-max_turns:]:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        prefix = "User" if role == "user" else "Assistant"
        history += f"{prefix}: {content}\n"
    return history



# Prompt Builder


def _profile_adaptation_block(state: dict) -> str:
    """Steer tone/pace/format from profile_agent; facts still come only from CONTEXT."""
    pv = state.get("profile_vector") or {}
    if not pv:
        return ""

    tags = pv.get("adaptation_tags") or []
    tags_s = ", ".join(tags) if tags else "none"
    reason = (pv.get("reasoning_summary") or "").strip()
    if len(reason) > 400:
        reason = reason[:400] + "…"

    return f"""
TEACHING PROFILE (adapt style only; do not invent facts—use CONTEXT for all substantive claims):
- Explanation style: {pv.get("preferred_explanation_style", "balanced")}
- Preferred format: {pv.get("preferred_format", "clear")}
- Examples domain: {pv.get("preferred_examples_domain", "general")}
- Pace: {pv.get("pace", "medium")}
- Adaptation tags: {tags_s}
{f"- Notes: {reason}" if reason else ""}
"""


def build_prompt(state: dict) -> str:

    query = state.get("query", "")
    intent = state.get("routing", {}).get("intent", "learn_concept")
    chunks = state.get("retrieved_chunks", [])
    summary = state.get("conversation_summary", "")
    history = build_history(state.get("session_history", []))

    context = build_context(chunks)
    profile_block = _profile_adaptation_block(state)

    # -------- Adaptive difficulty --------
    energy = state.get("energy_decision", {})
    mode = energy.get("mode", "balanced")

    difficulty = "medium"
    if mode == "light":
        difficulty = "easy"
    elif mode == "deep":
        difficulty = "hard"

    # -------- Intent-based behavior --------
    if intent == "practice":
        task_instruction = f"""
Generate EXACTLY 3 questions.

Return ONLY valid JSON:

[
  {{
    "question": "...",
    "answer": "...",
    "difficulty": "{difficulty}"
  }}
]

Rules:
- Use ONLY the context
- No extra text
"""

    elif intent == "revise":
        task_instruction = """
Provide:
1. A short summary
2. 3 revision questions with answers
"""

    elif intent == "mixed":
        task_instruction = """
Provide:
1. A clear explanation
2. 2 practice questions with answers
"""

    else:
        task_instruction = """
Provide a clear explanation with examples.
"""

    return f"""
You are an academic assistant.

STRICT RULES:
- Use ONLY the provided context
- Do NOT use outside knowledge
- If not found, say: "I don't know based on the course material"
{profile_block}

CONVERSATION SUMMARY:
{summary}

RECENT HISTORY:
{history}

{task_instruction}

CONTEXT:
{context}

CURRENT QUESTION:
{query}

ANSWER:
"""



# Source Formatter


def format_sources(chunks: List[Dict]) -> List[str]:
    seen = set()
    sources = []

    for i, c in enumerate(chunks):
        src = f"[{i+1}] {c.get('source_id')} (p.{c.get('metadata', {}).get('page', '?')})"
        if src not in seen:
            sources.append(src)
            seen.add(src)

    return sources



# Output Parser


def parse_output(answer: str, intent: str) -> Dict[str, Any]:

    if intent == "practice":
        try:
            return {
                "answer_type": "exercise",
                "content": json.loads(answer)
            }
        except:
            return {
                "answer_type": "exercise",
                "content": answer
            }

    elif intent == "revise":
        return {
            "answer_type": "summary_with_questions",
            "content": answer
        }

    elif intent == "mixed":
        return {
            "answer_type": "explanation_with_questions",
            "content": answer
        }

    return {
        "answer_type": "explanation",
        "content": answer
    }



# Conversation Summary Updater


def update_conversation_summary(llm, previous_summary: str, new_turn: str) -> str:
    prompt = f"""
Update the conversation summary.

Previous summary:
{previous_summary}

New interaction:
{new_turn}

Updated summary (keep it short and focused on learning progress):
"""
    response = llm.invoke(prompt)
    return response.content.strip()



# LEARNING AGENT NODE


def learning_agent(state: dict) -> dict:

    try:
        chunks = state.get("retrieved_chunks", [])
        intent = state.get("routing", {}).get("intent", "learn_concept")

        if not chunks:
            return {
                "final_response": "I couldn't find this in your course material.",
                "agent_runs": {
                    **state.get("agent_runs", {}),
                    "learning_agent": {"status": "no_context"}
                }
            }

        llm = get_llm()
        prompt = build_prompt(state)

        response = llm.invoke(prompt)
        answer = response.content.strip()

        parsed = parse_output(answer, intent)
        sources = format_sources(chunks)

        # ---- format response ----
        if intent == "practice" and isinstance(parsed["content"], list):
            final_response = parsed["content"]
            assistant_text = json.dumps(final_response)
        else:
            final_response = parsed["content"] + "\n\nSources:\n" + "\n".join(sources)
            assistant_text = final_response

        # =========================
        # UPDATE MEMORY
        # =========================

        session_history = state.get("session_history", [])

        session_history.append({
            "role": "user",
            "content": state.get("query", "")
        })

        session_history.append({
            "role": "assistant",
            "content": assistant_text
        })

        # Trim history
        MAX_HISTORY = 10
        session_history = session_history[-MAX_HISTORY:]

        # ---- update summary ----
        previous_summary = state.get("conversation_summary", "")

        new_turn = f"User: {state.get('query')} \nAssistant: {assistant_text}"

        updated_summary = update_conversation_summary(
            llm,
            previous_summary,
            new_turn
        )

        return {
            "final_response": final_response,
            "session_history": session_history,
            "conversation_summary": updated_summary,

            "response_draft": {
                "answer_type": parsed["answer_type"],
                "structure": "contextual_rag",
                "tone": "adaptive",
            },

            "agent_runs": {
                **state.get("agent_runs", {}),
                "learning_agent": {"status": "success"}
            }
        }

    except Exception as e:
        return {
            "final_response": "Something went wrong.",
            "errors": state.get("errors", []) + [str(e)],
            "agent_runs": {
                **state.get("agent_runs", {}),
                "learning_agent": {
                    "status": "failed",
                    "error": str(e)
                }
            }
        }