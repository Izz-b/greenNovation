from typing import Dict, List
from langchain_groq import ChatGroq

# LLM

def get_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.3
    )

# Context Builder 


MAX_CHARS = 800  # prevent token overflow

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
    chunks = state.get("retrieved_chunks", [])
    energy = state.get("energy_decision", {})
    profile = state.get("profile_vector", {})
    readiness = state.get("readiness_signal", {})

    context = build_context(chunks)

    # ---- adapt depth ----
    depth = energy.get("response_depth", "medium")

    if depth == "short":
        instruction = "Give a short, clear explanation."
    elif depth == "long":
        instruction = "Give a detailed explanation with examples."
    else:
        instruction = "Give a clear and structured explanation."

    # ---- adapt tone ----
    tone = "supportive and clear"

    if readiness.get("behavioral_fatigue_band") == "high":
        tone = "very supportive, reassuring, and simple"

    # ---- learning style ----
    style = profile.get("preferred_explanation_style", "simple")

    return f"""
You are an academic AI assistant helping a university student.

RULES:
- Answer ONLY using the provided context
- Do NOT use prior knowledge
- If the answer is missing, say EXACTLY: "I don't know based on the course material"
- Cite sources using [number] inline

STYLE:
- Explanation style: {style}
- {instruction}
- Be {tone}

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:
"""

# Post-processing


def format_sources(chunks: List[Dict]) -> List[str]:
    seen = set()
    sources = []

    for i, c in enumerate(chunks):
        src = f"[{i+1}] {c.get('source_id')} (p.{c.get('metadata', {}).get('page', '?')})"
        if src not in seen:
            sources.append(src)
            seen.add(src)

    return sources

# LEARNING AGENT NODE

def learning_agent(state: dict) -> dict:
    """
    Uses RAG + signals to generate final answer.
    """

    try:
        chunks = state.get("retrieved_chunks", [])

        #  fallback if no context
        if not chunks:
            return {
                "final_response": "I don't know based on the course material.",
                "agent_runs": {
                    **state.get("agent_runs", {}),
                    "learning_agent": {
                        "status": "no_context"
                    }
                }
            }

        llm = get_llm()
        prompt = build_prompt(state)

        
        response = llm.invoke([
            {"role": "system", "content": "You are an academic AI assistant."},
            {"role": "user", "content": prompt}
        ])

        answer = response.content.strip()
        sources = format_sources(chunks)

        final_response = answer + "\n\nSources:\n" + "\n".join(sources)

        return {
            "final_response": final_response,

            "response_draft": {
                "answer_type": "explanation",
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