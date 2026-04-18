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



# Prompt Builder


def build_prompt(state: dict) -> str:

    query = state.get("query", "")
    intent = state.get("routing", {}).get("intent", "learn_concept")
    chunks = state.get("retrieved_chunks", [])

    context = build_context(chunks)

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

Return ONLY valid JSON (no text before or after):

[
  {{
    "question": "...",
    "answer": "...",
    "difficulty": "{difficulty}"
  }}
]

Rules:
- Use ONLY the context
- Do NOT add explanations
- Do NOT add markdown
- Do NOT add comments
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

    else:  # learn_concept
        task_instruction = """
Provide a clear explanation with examples.
"""

    return f"""
You are an academic assistant.

STRICT RULES:
- Use ONLY the provided context
- Do NOT use outside knowledge
- If the answer is not in the context, say:
  "I don't know based on the course material"

{task_instruction}

CONTEXT:
{context}

QUESTION:
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
            parsed_json = json.loads(answer)
            return {
                "answer_type": "exercise",
                "content": parsed_json
            }
        except:
            return {
                "answer_type": "exercise",
                "content": answer  # fallback if JSON breaks
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

    else:
        return {
            "answer_type": "explanation",
            "content": answer
        }



# LEARNING AGENT NODE


def learning_agent(state: dict) -> dict:
    """
    Main generation agent (LLM call).
    """

    try:
        chunks = state.get("retrieved_chunks", [])
        intent = state.get("routing", {}).get("intent", "learn_concept")

        # ---- No context fallback ----
        if not chunks:
            return {
                "final_response": "I couldn't find this in your course material. Try rephrasing your question.",
                "agent_runs": {
                    **state.get("agent_runs", {}),
                    "learning_agent": {
                        "status": "no_context"
                    }
                }
            }

        llm = get_llm()
        prompt = build_prompt(state)

        response = llm.invoke(prompt)
        answer = response.content.strip()

        parsed = parse_output(answer, intent)
        sources = format_sources(chunks)

        # ---- Format final response ----
        if intent == "practice" and isinstance(parsed["content"], list):
            final_response = parsed["content"]  # JSON → frontend handles it
        else:
            final_response = parsed["content"] + "\n\nSources:\n" + "\n".join(sources)

        return {
            "final_response": final_response,

            "response_draft": {
                "answer_type": parsed["answer_type"],
                "structure": "contextual_rag",
                "tone": "adaptive",
            },

            "agent_runs": {
                **state.get("agent_runs", {}),
                "learning_agent": {
                    "status": "success"
                }
            }
        }

    except Exception as e:
        return {
            "final_response": "Something went wrong while generating the answer.",
            "errors": state.get("errors", []) + [f"learning_agent error: {str(e)}"],
            "agent_runs": {
                **state.get("agent_runs", {}),
                "learning_agent": {
                    "status": "failed",
                    "error": str(e)
                }
            }
        }