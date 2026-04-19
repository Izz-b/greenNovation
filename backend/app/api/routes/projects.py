from fastapi import APIRouter

from backend.app.schemas.project import Project, ProjectsPayload
from backend.app.services import projects_service

router = APIRouter(tags=["projects"])


@router.get("/api/projects")
def get_projects():
    return ProjectsPayload(projects=projects_service.load_projects())


@router.put("/api/projects")
def put_projects(body: ProjectsPayload):
    projects_service.save_projects(list(body.projects))
    return ProjectsPayload(projects=body.projects)
