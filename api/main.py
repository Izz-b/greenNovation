"""
FastAPI entrypoint: runs orchestrator → learning pipeline for chat turns.

Run from repo root (greenNovation):
  pip install -e ".[api]"
  uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

Env: GROQ_API_KEY (required for learning agent). Optional: GREENNOVATION_DATA_DIR, MISTRAL_API_KEY / profile keys.
"""

from __future__ import annotations

import copy
import os
import uuid
from pathlib import Path

import mimetypes

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Repo root (greenNovation/) — RAG and .env resolve from here
_ROOT = Path(__file__).resolve().parent.parent
os.environ.setdefault("GREENNOVATION_DATA_DIR", str(_ROOT / "data"))
load_dotenv(_ROOT / ".env")

from ai.graph.learning_workflow import run_learning_pipeline  # noqa: E402


def _default_session_state() -> dict:
    return {
        "session_history": [],
        "session_action": "continue",
        "conversation_summary": "",
        "readiness_signal": {"behavioral_fatigue_band": "low"},
        "calendar_events": [],
        "course_context": {},
        "agent_runs": {},
        "errors": [],
        "traces": [],
        "warnings": [],
        "metrics": {},
        "passive_behavior_signals": {
            "tasks_due_3d": 2,
            "overdue_tasks": 0,
            "project_risk_level": "low",
            "study_sessions_last_7d": 5,
            "avg_session_completion_rate": 0.8,
            "avg_quiz_score_trend": 4.0,
            "late_night_activity_ratio": 0.1,
            "long_sessions_without_breaks": 0,
        },
    }


# Ephemeral keys not stored between HTTP turns
_EPHEMERAL = frozenset(
    {
        "traces",
        "retrieved_chunks",
        "merged_signal_bundle",
        "response_draft",
        "query",
        "final_response",
    }
)


def _persistable_state(state: dict) -> dict:
    out = copy.deepcopy(state)
    for k in _EPHEMERAL:
        out.pop(k, None)
    return out


_sessions: dict[str, dict] = {}

_INDEX_FILES = frozenset({"index.faiss", "index.pkl"})


def _data_dir_path() -> Path:
    return Path(os.environ["GREENNOVATION_DATA_DIR"]).resolve()


def _safe_data_file(filename: str) -> Path | None:
    if not filename or filename in (".", ".."):
        return None
    if "/" in filename or "\\" in filename:
        return None
    base = _data_dir_path()
    path = (base / filename).resolve()
    try:
        path.relative_to(base)
    except ValueError:
        return None
    if not path.is_file():
        return None
    return path


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


def _reply_to_text(final_response: object) -> tuple[str, str | list | None]:
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


app = FastAPI(title="greenNovation API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:8080,http://localhost:8081,http://127.0.0.1:5501,http://localhost:5501",
    ).split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/corpus/files")
def list_corpus_files():
    base = _data_dir_path()
    if not base.is_dir():
        return {"data_dir": str(base), "files": [], "error": "data directory does not exist"}
    out: list[dict] = []
    for p in sorted(base.iterdir()):
        if not p.is_file():
            continue
        name = p.name
        kind = "rag_index" if name in _INDEX_FILES else "document"
        out.append({"name": name, "size_bytes": p.stat().st_size, "kind": kind})
    return {"data_dir": str(base), "files": out}


@app.get("/api/corpus/file/{filename}")
def get_corpus_file(filename: str):
    path = _safe_data_file(filename)
    if path is None:
        raise HTTPException(status_code=404, detail="File not found")
    media = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return FileResponse(path, filename=path.name, media_type=media)


@app.get("/health")
def health():
    data_dir = Path(os.environ["GREENNOVATION_DATA_DIR"])
    return {
        "status": "ok",
        "data_dir": str(data_dir),
        "data_dir_exists": data_dir.is_dir(),
        "groq_configured": bool(os.environ.get("GROQ_API_KEY")),
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    sid = req.session_id or str(uuid.uuid4())
    base = _sessions.get(sid)
    if base is None:
        base = _default_session_state()
    else:
        base = copy.deepcopy(base)

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
    text, raw = _reply_to_text(final)
    _sessions[sid] = _persistable_state(state)

    return ChatResponse(
        session_id=sid,
        reply=text or "No response generated.",
        reply_raw=raw,
        routing=state.get("routing"),
        errors=list(state.get("errors") or []),
        warnings=list(state.get("warnings") or []),
    )


@app.delete("/api/session/{session_id}")
def clear_session(session_id: str):
    _sessions.pop(session_id, None)
    return {"ok": True}
