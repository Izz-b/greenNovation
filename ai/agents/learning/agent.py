from typing import Dict, List, Any
from langchain_groq import ChatGroq
import json
from json import JSONDecodeError

from ai.state.agent_context import AgentContext


# LLM (ENERGY-AWARE)

def get_llm(energy: dict):
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=energy.get("temperature", 0.3),
        max_tokens=energy.get("max_tokens", 500)
    )


# CONTEXT BUILDER


MAX_CHARS = 800

def build_context(chunks: List[Dict], max_chars: int) -> str:
    context = ""

    for i, c in enumerate(chunks):
        source = c.get("source_id", "unknown")
        page = c.get("metadata", {}).get("page", "?")
        content = c.get("content", "")[:max_chars]

        context += f"[{i+1}] ({source}, p.{page})\n{content}\n\n"

    return context



# HISTORY BUILDER


def build_history(session_history: List[Dict], max_turns: int = 5) -> str:
    history = ""
    for turn in session_history[-max_turns:]:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        prefix = "User" if role == "user" else "Assistant"
        history += f"{prefix}: {content}\n"
    return history



# PROFILE ADAPTATION


def _profile_adaptation_block(state: dict) -> str:
    pv = state.get("profile_vector") or {}
    if not pv:
        return ""

    tags = pv.get("adaptation_tags") or []
    tags_s = ", ".join(tags) if tags else "none"
    reason = (pv.get("reasoning_summary") or "").strip()

    if len(reason) > 400:
        reason = reason[:400] + "…"

    return f"""
TEACHING STYLE (adapt tone/format only):
- Explanation style: {pv.get("preferred_explanation_style", "balanced")}
- Format: {pv.get("preferred_format", "clear")}
- Examples domain: {pv.get("preferred_examples_domain", "general")}
- Pace: {pv.get("pace", "medium")}
- Tags: {tags_s}
{f"- Notes: {reason}" if reason else ""}
"""


def _readiness_adaptation_block(state: AgentContext) -> str:
    """Steer workload/tone based on readiness signal."""
    readiness = state.get("readiness_signal") or {}
    if not readiness:
        return ""

    reason = (readiness.get("reasoning_summary") or "").strip()
    if len(reason) > 400:
        reason = reason[:400] + "..."

    return f"""
READINESS SIGNAL (adapt teaching load and tone):
- Recommended intensity: {readiness.get("recommended_intensity", "normal")}
- Suggested session minutes: {readiness.get("suggested_session_minutes", 30)}
- Difficulty adjustment: {readiness.get("difficulty_adjustment", "keep")}
- Break recommendation: {readiness.get("break_recommendation", False)}
- Support tone: {readiness.get("support_tone", "neutral")}
{f"- Notes: {reason}" if reason else ""}
"""


def _derive_behavior_settings(state: AgentContext) -> Dict[str, Any]:
    """Derive final behavior controls from energy + readiness signals."""
    energy = state.get("energy_decision") or {}
    readiness = state.get("readiness_signal") or {}

    energy_mode = energy.get("mode", "balanced")
    difficulty = "medium"
    if energy_mode == "light":
        difficulty = "easy"
    elif energy_mode == "deep":
        difficulty = "hard"

    difficulty_adj = readiness.get("difficulty_adjustment")
    if difficulty_adj == "decrease":
        difficulty = "easy"
    elif difficulty_adj == "increase":
        difficulty = "hard"

    support_tone = readiness.get("support_tone", "neutral")
    style_hint = {
        "supportive": "Use empathetic and encouraging language.",
        "challenging": "Use direct coaching language with stretch prompts.",
    }.get(support_tone, "Use neutral, clear, and concise language.")

    suggested_minutes = readiness.get("suggested_session_minutes", 30)
    break_needed = readiness.get("break_recommendation", False)

    return {
        "difficulty": difficulty,
        "support_tone": support_tone,
        "style_hint": style_hint,
        "suggested_minutes": suggested_minutes,
        "break_needed": break_needed,
    }


def build_prompt(state: dict) -> str:

    query = state.get("query", "")
    intent = state.get("routing", {}).get("intent", "learn_concept")
    chunks = state.get("retrieved_chunks", [])
    summary = state.get("conversation_summary", "")
    history = build_history(state.get("session_history", []))

    energy = state.get("energy_decision", {})

    context = build_context(
        chunks,
        energy.get("chunk_truncation_chars", MAX_CHARS)
    )

    profile_block = _profile_adaptation_block(state)
    readiness_block = _readiness_adaptation_block(state)
    behavior = _derive_behavior_settings(state)
    difficulty = behavior["difficulty"]
    style_hint = behavior["style_hint"]
    suggested_minutes = behavior["suggested_minutes"]
    break_needed = behavior["break_needed"]

    # ENERGY CONTROLS


    mode = energy.get("mode", "balanced")
    generate_quiz = energy.get("generate_quiz", True)
    depth = energy.get("response_depth", "medium")


    # response length
    if depth == "short":
        length_instruction = "Keep the answer VERY concise."
    elif depth == "long":
        length_instruction = "Provide a detailed explanation."
    else:
        length_instruction = "Provide a balanced explanation."


    # TASK LOGIC
 

    if intent == "practice" and generate_quiz:
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

    elif intent == "practice" and not generate_quiz:
        task_instruction = """
Explain the concept instead of generating questions (energy-saving mode).
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
        task_instruction = "Provide a clear explanation with examples."

    return f"""
You are an academic assistant.

STRICT RULES:
- Use ONLY the provided context
- Do NOT use outside knowledge
- If not found, say: "I don't know based on the course material"

{profile_block}
{readiness_block}
BEHAVIOR RULES:
- {style_hint}
- Target response depth appropriate for a {suggested_minutes}-minute study session.
- {"Include a short break reminder at the end." if break_needed else "No break reminder needed unless user asks."}

CONVERSATION SUMMARY:
{summary}

RECENT HISTORY:
{history}

{length_instruction}

{task_instruction}

CONTEXT:
{context}

CURRENT QUESTION:
{query}

ANSWER:
"""


# SOURCE FORMATTER


def format_sources(chunks: List[Dict]) -> List[str]:
    seen = set()
    sources = []

    for i, c in enumerate(chunks):
        src = f"[{i+1}] {c.get('source_id')} (p.{c.get('metadata', {}).get('page', '?')})"
        if src not in seen:
            sources.append(src)
            seen.add(src)

    return sources



# OUTPUT PARSER


def parse_output(answer: str, intent: str) -> Dict[str, Any]:

    if intent == "practice":
        try:
            return {
                "answer_type": "exercise",
                "content": json.loads(answer)
            }
        except JSONDecodeError:
            return {
                "answer_type": "exercise",
                "content": answer
            }

    elif intent == "revise":
        return {"answer_type": "summary_with_questions", "content": answer}

    elif intent == "mixed":
        return {"answer_type": "explanation_with_questions", "content": answer}

    return {"answer_type": "explanation", "content": answer}


# SUMMARY UPDATE (OPTIMIZED)

def update_conversation_summary(llm, previous_summary: str, new_turn: str) -> str:
    prompt = f"""
Update the conversation summary.

Previous summary:
{previous_summary}

New interaction:
{new_turn}

Updated summary (short, focused on learning progress):
"""
    response = llm.invoke(prompt)
    return response.content.strip()


# LEARNING AGENT NODE

def learning_agent(state: AgentContext) -> AgentContext:

    try:
        chunks = state.get("retrieved_chunks", [])
        intent = state.get("routing", {}).get("intent", "learn_concept")
        behavior = _derive_behavior_settings(state)
        energy = state.get("energy_decision", {})

        # ---- fallback ----
        if not chunks:
            return {
                "final_response": "I couldn't find this in your course material.",
                "agent_runs": {
                    **state.get("agent_runs", {}),
                    "learning_agent": {"status": "no_context"}
                }
            }

        llm = get_llm(energy)
        prompt = build_prompt(state)

        response = llm.invoke(prompt)
        answer = response.content.strip()

        parsed = parse_output(answer, intent)
        sources = format_sources(chunks)

        include_sources = energy.get("include_sources", True)

        # =========================
        # FINAL RESPONSE
        # =========================

        if intent == "practice" and isinstance(parsed["content"], list):
            final_response = parsed["content"]
            assistant_text = json.dumps(final_response)

        else:
            if include_sources:
                final_response = parsed["content"] + "\n\nSources:\n" + "\n".join(sources)
            else:
                final_response = parsed["content"]

            assistant_text = final_response

        # =========================
        # MEMORY UPDATE
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

        session_history = session_history[-10:]

        # =========================
        # SUMMARY UPDATE (ENERGY-AWARE)
        # =========================

        previous_summary = state.get("conversation_summary", "")

        should_update_summary = (
            energy.get("mode") != "light" and
            len(session_history) % 4 == 0
        )

        if should_update_summary:
            new_turn = f"User: {state.get('query')} \nAssistant: {assistant_text}"

            updated_summary = update_conversation_summary(
                llm,
                previous_summary,
                new_turn
            )
        else:
            updated_summary = previous_summary

        return {
            "final_response": final_response,
            "session_history": session_history,
            "conversation_summary": updated_summary,

            "response_draft": {
                "answer_type": parsed["answer_type"],
                "structure": "contextual_rag",
                "tone": behavior["support_tone"],
            },

            "agent_runs": {
                **state.get("agent_runs", {}),
                "learning_agent": {
                    "status": "success",
                    "mode": energy.get("mode", "balanced")
                }
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