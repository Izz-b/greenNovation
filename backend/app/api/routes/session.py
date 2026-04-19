from fastapi import APIRouter

from backend.app.services.session_service import delete_session

router = APIRouter(tags=["session"])


@router.delete("/api/session/{session_id}")
def clear_session(session_id: str):
    delete_session(session_id)
    return {"ok": True}
