"""API routes for forest/tree gamification."""

from fastapi import APIRouter, HTTPException
from backend.app.schemas.forest import (
    ForestResponse,
    InventoryResponse,
    PlantTreeRequest,
    PlantTreeResponse,
    AwardTreeRequest,
    AwardTreeResponse,
)
from backend.app.services.forest_service import ForestService

router = APIRouter(prefix="/api/forest", tags=["forest"])


@router.get("/forest", response_model=ForestResponse)
def get_forest():
    """Get current user's forest state with all planted trees."""
    user_id = "default_user"  # TODO: extract from JWT
    return ForestService.get_forest(user_id)


@router.get("/inventory", response_model=InventoryResponse)
def get_inventory():
    """Get current user's tree inventory count."""
    user_id = "default_user"  # TODO: extract from JWT
    return ForestService.get_inventory(user_id)


@router.post("/plant", response_model=PlantTreeResponse)
def plant_tree(req: PlantTreeRequest):
    """Plant a tree in the forest (consumes one tree from inventory)."""
    user_id = "default_user"  # TODO: extract from JWT
    try:
        return ForestService.plant_tree(user_id, req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/award", response_model=AwardTreeResponse)
def award_tree(req: AwardTreeRequest):
    """Award a tree to the user (adds to inventory)."""
    user_id = "default_user"  # TODO: extract from JWT
    return ForestService.award_tree(user_id, req)


@router.get("/stats")
def get_stats():
    """Get global forest statistics."""
    return ForestService.get_stats()
