"""Business logic for forest/tree gamification system."""

from datetime import datetime
from uuid import uuid4
from collections import defaultdict
from backend.app.schemas.forest import (
    TreeModel,
    ForestResponse,
    InventoryResponse,
    PlantTreeRequest,
    PlantTreeResponse,
    AwardTreeRequest,
    AwardTreeResponse,
    TreeKind,
)


# In-memory storage: user_id -> {forest, inventory}
# In production, replace with actual database
_forests: dict[str, list[TreeModel]] = defaultdict(list)
_inventories: dict[str, int] = defaultdict(lambda: 2)  # Start with 2 trees
_total_earned: dict[str, int] = defaultdict(int)
_reward_history: dict[str, set[str]] = defaultdict(set)  # For deduplication


class ForestService:
    """Manages tree planting and forest state."""

    @staticmethod
    def get_forest(user_id: str) -> ForestResponse:
        """Get user's forest state with streak from readiness check-ins."""
        trees = _forests.get(user_id, [])
        total = _total_earned.get(user_id, 0)
        
        # Calculate streak locally to avoid circular imports
        streak = ForestService._calculate_streak(user_id)
        
        return ForestResponse(
            trees=trees,
            total_trees=len(trees),
            streak_days=streak,
        )
    
    @staticmethod
    def _calculate_streak(user_id: str) -> int:
        """
        Calculate the current check-in streak (consecutive days with check-ins).
        
        Counts backwards from today to find consecutive days with at least one check-in.
        Import readiness_service inside method to avoid circular dependency.
        """
        from datetime import timedelta
        from backend.app.services.readiness_service import _checkins
        
        checkins = _checkins.get(user_id, [])
        if not checkins:
            return 0
        
        # Group check-ins by date
        dates_with_checkins = set()
        for checkin in checkins:
            dates_with_checkins.add(checkin["date"])
        
        # Count backwards from today
        streak = 0
        current_date = datetime.utcnow().date()
        
        while current_date.strftime("%Y-%m-%d") in dates_with_checkins:
            streak += 1
            current_date -= timedelta(days=1)
        
        return streak

    @staticmethod
    def plant_tree(user_id: str, req: PlantTreeRequest) -> PlantTreeResponse:
        """Plant a tree in the user's forest (consumes inventory)."""
        # Check inventory
        inventory = _inventories.get(user_id, 0)
        if inventory <= 0:
            raise ValueError("No trees available to plant")

        # Create tree
        tree = TreeModel(
            id=str(uuid4()),
            kind=req.kind,
            x=req.x,
            y=req.y,
            scale=req.scale,
            planted_at=datetime.now(),
        )

        # Add to forest and consume inventory
        _forests[user_id].append(tree)
        _inventories[user_id] = inventory - 1

        return PlantTreeResponse(
            tree=tree,
            remaining_inventory=_inventories[user_id],
        )

    @staticmethod
    def get_inventory(user_id: str) -> InventoryResponse:
        """Get user's tree inventory."""
        available = _inventories[user_id]  # Use defaultdict to get default value
        total = _total_earned.get(user_id, 0)
        return InventoryResponse(
            available=available,
            total_earned=total,
            last_reward=None,  # TODO: track last reward with timestamp
        )

    @staticmethod
    def award_tree(user_id: str, req: AwardTreeRequest) -> AwardTreeResponse:
        """Award a tree to user (adds to inventory)."""
        # Deduplication: check if this reward already granted
        if req.dedupe_key:
            history = _reward_history.get(user_id, set())
            if req.dedupe_key in history:
                # Already awarded, return current state
                return AwardTreeResponse(
                    available=_inventories.get(user_id, 0),
                    message=f"Tree already awarded for: {req.message}",
                )
            # Mark as awarded
            history.add(req.dedupe_key)
            _reward_history[user_id] = history

        # Award the tree
        _inventories[user_id] = _inventories.get(user_id, 0) + 1
        _total_earned[user_id] = _total_earned.get(user_id, 0) + 1

        return AwardTreeResponse(
            available=_inventories[user_id],
            message=f"🌱 Tree earned! {req.message}",
        )

    @staticmethod
    def get_stats() -> dict:
        """Get global forest stats (aggregate across all users)."""
        total_users = len(_forests)
        total_trees = sum(len(trees) for trees in _forests.values())
        total_inventory = sum(_inventories.values())
        
        # CO2 estimate: ~20kg per tree
        co2_saved = total_trees * 0.2

        return {
            "total_users": total_users,
            "total_trees_planted": total_trees,
            "total_trees_available": total_inventory,
            "estimated_co2_saved_kg": round(co2_saved, 1),
        }
