import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

export type TreeKind = "oak" | "pine" | "blossom" | "bamboo" | "sapling";

export interface TreeModel {
  id: string;
  kind: TreeKind;
  x: number;
  y: number;
  scale: number;
  planted_at: string;
}

export interface ForestResponse {
  trees: TreeModel[];
  total_trees: number;
  streak_days: number;
}

export interface InventoryResponse {
  available: number;
  total_earned: number;
  last_reward: null | { id: string; reason: string; message: string; earnedAt: number };
}

export interface PlantTreeRequest {
  kind: TreeKind;
  x: number;
  y: number;
  scale: number;
}

export interface PlantTreeResponse {
  tree: TreeModel;
  remaining_inventory: number;
}

export interface AwardTreeRequest {
  reason: "daily" | "project" | "manual";
  message: string;
  dedupe_key?: string;
}

export interface AwardTreeResponse {
  available: number;
  message: string;
}

/**
 * Get user's forest state with all planted trees
 */
export function useForest() {
  return useQuery({
    queryKey: ["forest"],
    queryFn: async (): Promise<ForestResponse> => {
      const resp = await fetch(`/api/forest/forest`);
      if (!resp.ok) throw new Error("Failed to fetch forest");
      return resp.json();
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Get user's tree inventory count
 */
export function useForestInventory() {
  return useQuery({
    queryKey: ["forest-inventory"],
    queryFn: async (): Promise<InventoryResponse> => {
      const resp = await fetch(`/api/forest/inventory`);
      if (!resp.ok) throw new Error("Failed to fetch inventory");
      return resp.json();
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

/**
 * Plant a tree (mutation)
 */
export function usePlantTree() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (req: PlantTreeRequest): Promise<PlantTreeResponse> => {
      const resp = await fetch(`/api/forest/plant`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
      });
      if (!resp.ok) throw new Error("Failed to plant tree");
      return resp.json();
    },
    onSuccess: () => {
      // Invalidate both queries so they refetch with new data
      queryClient.invalidateQueries({ queryKey: ["forest"] });
      queryClient.invalidateQueries({ queryKey: ["forest-inventory"] });
    },
  });
}

/**
 * Award a tree to user (adds to inventory)
 */
export function useAwardTree() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (req: AwardTreeRequest): Promise<AwardTreeResponse> => {
      const resp = await fetch(`/api/forest/award`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
      });
      if (!resp.ok) throw new Error("Failed to award tree");
      return resp.json();
    },
    onSuccess: () => {
      // Invalidate inventory query so it refetches with new count
      queryClient.invalidateQueries({ queryKey: ["forest-inventory"] });
    },
  });
}

/**
 * Get global forest statistics
 */
export function useForestStats() {
  return useQuery({
    queryKey: ["forest-stats"],
    queryFn: async () => {
      const resp = await fetch(`/api/forest/stats`);
      if (!resp.ok) throw new Error("Failed to fetch stats");
      return resp.json();
    },
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}
