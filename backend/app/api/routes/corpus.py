import mimetypes

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.app.services.corpus_service import list_corpus_files, safe_data_file

router = APIRouter(tags=["corpus"])


@router.get("/api/corpus/files")
def corpus_files():
    return list_corpus_files()


@router.get("/api/corpus/file/{filename}")
def corpus_file(filename: str):
    path = safe_data_file(filename)
    if path is None:
        raise HTTPException(status_code=404, detail="File not found")
    media = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return FileResponse(path, filename=path.name, media_type=media)
