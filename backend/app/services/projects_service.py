from __future__ import annotations

import json
import os
from pathlib import Path

from backend.app.schemas.project import Project, ProjectsPayload

_PROJECTS_FILE = "projects.json"


def _path() -> Path:
    return Path(os.environ["GREENNOVATION_DATA_DIR"]).resolve() / _PROJECTS_FILE


def load_projects() -> list[Project]:
    p = _path()
    if not p.is_file():
        return []
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    try:
        payload = ProjectsPayload.model_validate(raw)
    except Exception:
        return []
    return payload.projects


def save_projects(projects: list[Project]) -> None:
    p = _path()
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = ProjectsPayload(projects=projects)
    p.write_text(payload.model_dump_json(indent=2), encoding="utf-8")
