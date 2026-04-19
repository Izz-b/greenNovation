from __future__ import annotations

import os
from pathlib import Path

_INDEX_FILES = frozenset({"index.faiss", "index.pkl"})


def data_dir_path() -> Path:
    return Path(os.environ["GREENNOVATION_DATA_DIR"]).resolve()


def safe_data_file(filename: str) -> Path | None:
    if not filename or filename in (".", ".."):
        return None
    if "/" in filename or "\\" in filename:
        return None
    base = data_dir_path()
    path = (base / filename).resolve()
    try:
        path.relative_to(base)
    except ValueError:
        return None
    if not path.is_file():
        return None
    return path


def list_corpus_files() -> dict:
    base = data_dir_path()
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
