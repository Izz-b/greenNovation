from __future__ import annotations

import uuid

from ai.graph.learning_workflow import run_learning_pipeline

from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services import session_service as sessions


def reply_to_text(final_response: object) -> tuple[str, str | list | None]:
    if isinstance(final_response, list):
        raw: str | list | None = final_response
        lines = []
        for i, item in enumerate(final_response):
            if isinstance(item, dict):
                q = item.get("question", "")
                a = item.get("answer", "")
                lines.append(f"**Q{i + 1}** {q}\n*Answer:* {a}")
            else:
                lines.append(str(item))
        return "\n\n".join(lines), raw
    if final_response is None:
        return "", None
    return str(final_response), str(final_response)


async def chat_turn(req: ChatRequest) -> ChatResponse:
    sid = req.session_id or str(uuid.uuid4())
    base = sessions.load_session_copy(sid) or sessions.default_session_state()

    base["query"] = req.message.strip()
    if req.intent:
        base["routing"] = {"intent": req.intent}
    else:
        base["routing"] = {"intent": "unknown"}
    base["session_action"] = "continue"
    if req.passive_behavior_signals:
        base["passive_behavior_signals"] = req.passive_behavior_signals
    if req.course_context:
        base["course_context"] = {**(base.get("course_context") or {}), **req.course_context}

    try:
        state = await run_learning_pipeline(base)
    except Exception as e:
        return ChatResponse(
            session_id=sid,
            reply=f"The AI pipeline failed: {e}",
            reply_raw=None,
            routing=None,
            errors=[str(e)],
            warnings=[],
        )

    final = state.get("final_response")
    text, raw = reply_to_text(final)
    sessions.save_session(sid, state)

    return ChatResponse(
        session_id=sid,
        reply=text or "No response generated.",
        reply_raw=raw,
        routing=state.get("routing"),
        errors=list(state.get("errors") or []),
        warnings=list(state.get("warnings") or []),
    )
