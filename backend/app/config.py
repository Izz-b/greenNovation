"""Paths and environment (load before importing `ai.*`)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


def repo_root() -> Path:
    """greenNovation/ (parent of `backend/`)."""
    return Path(__file__).resolve().parent.parent.parent


def bootstrap() -> None:
    root = repo_root()
    os.environ.setdefault("GREENNOVATION_DATA_DIR", str(root / "data"))
    load_dotenv(root / ".env")
