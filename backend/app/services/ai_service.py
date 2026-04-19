from __future__ import annotations

import uuid

from ai.graph.learning_workflow import run_learning_pipeline

from backend.app.schemas.chat import ChatRequest, ChatResponse, EnergySnapshot, SessionInsightsPayload
from backend.app.services import session_service as sessions


def _energy_to_snapshot(state: dict) -> EnergySnapshot | None:
    """Expose energy agent decision for the workspace sidebar."""
    ed = state.get("energy_decision") or {}
    if not isinstance(ed, dict) or not ed:
        return None
    return EnergySnapshot(
        mode=str(ed.get("mode", "unknown")),
        responseDepth=str(ed.get("response_depth", "medium")),
        maxTokens=int(ed.get("max_tokens", 400)),
        reason=str(ed.get("reason", ""))[:600],
        reuseCachedAnswer=bool(ed.get("reuse_cached_answer")),
        reuseCachedRag=bool(ed.get("reuse_cached_rag")),
        reuseReadinessSignal=bool(ed.get("reuse_readiness_signal")),
    )


def _readiness_to_session_insights(state: dict) -> SessionInsightsPayload | None:
    """Expose readiness adaptation fields for the frontend Live insights column."""
    rs = state.get("readiness_signal") or {}
    sm = rs.get("suggested_session_minutes")
    br = rs.get("break_recommendation")
    da = rs.get("difficulty_adjustment")
    kwargs: dict[str, str] = {}
    if isinstance(sm, int):
        kwargs["sessionMinutes"] = f"{sm} minutes"
    if isinstance(br, bool):
        kwargs["breakNeeded"] = "Yes" if br else "No"
    if isinstance(da, str) and da.strip():
        kwargs["difficultyAdjustment"] = da.strip().capitalize()
    if not kwargs:
        return None
    return SessionInsightsPayload(**kwargs)


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
    if req.prompt_hint:
        base["prompt_hint"] = req.prompt_hint
    else:
        base.pop("prompt_hint", None)
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
            energy=None,
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
        session_insights=_readiness_to_session_insights(state),
        energy=_energy_to_snapshot(state),
    )
