from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    session_id: str | None = None
    """Omit to start a new session."""
    intent: str | None = Field(
        default=None,
        description="Optional: learn_concept, practice, revise, plan_study, wellbeing_check — else orchestrator infers from text.",
    )
    passive_behavior_signals: dict | None = None
    course_context: dict | None = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    reply_raw: str | list | None = None
    routing: dict | None = None
    errors: list[str] = []
    warnings: list[str] = []
