"""Pydantic models for forest/tree gamification system."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

TreeKind = Literal["oak", "pine", "blossom", "bamboo", "sapling"]
RewardReason = Literal["daily", "project", "manual"]


class TreeModel(BaseModel):
    """Single tree planted in the forest."""
    id: str = Field(..., description="Unique tree ID")
    kind: TreeKind = Field(..., description="Tree species")
    x: float = Field(..., ge=0, le=100, description="X position (0-100%)")
    y: float = Field(..., ge=0, le=100, description="Y position (0-100%)")
    scale: float = Field(..., gt=0, description="Size scale multiplier")
    planted_at: datetime = Field(..., description="When tree was planted")


class ForestResponse(BaseModel):
    """User's current forest state."""
    trees: list[TreeModel] = Field(default_factory=list, description="All planted trees")
    total_trees: int = Field(default=0, description="Total trees ever planted")
    streak_days: int = Field(default=0, description="Daily login streak")


class InventoryResponse(BaseModel):
    """Tree inventory state."""
    available: int = Field(default=0, description="Trees ready to plant")
    total_earned: int = Field(default=0, description="Lifetime trees earned")
    last_reward: dict | None = Field(default=None, description="Most recent tree earned")


class PlantTreeRequest(BaseModel):
    """Request to plant a tree."""
    kind: TreeKind = Field(..., description="Tree species")
    x: float = Field(..., ge=0, le=100, description="X position (0-100%)")
    y: float = Field(..., ge=0, le=100, description="Y position (0-100%)")
    scale: float = Field(default=0.85, gt=0, description="Size scale")


class PlantTreeResponse(BaseModel):
    """Response after planting a tree."""
    tree: TreeModel = Field(..., description="Newly planted tree")
    remaining_inventory: int = Field(..., description="Trees left to plant")


class AwardTreeRequest(BaseModel):
    """Request to award a tree to user."""
    reason: RewardReason = Field(..., description="Why the tree was earned")
    message: str = Field(..., description="Human-readable award message")
    dedupe_key: str | None = Field(default=None, description="Optional dedup key (e.g., 'daily-2026-04-19')")


class AwardTreeResponse(BaseModel):
    """Response after awarding a tree."""
    available: int = Field(..., description="New inventory count")
    message: str = Field(..., description="Confirmation message")
