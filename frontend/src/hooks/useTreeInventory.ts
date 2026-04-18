import { useEffect, useState } from "react";
import { subscribeInventory, type TreeReward } from "@/lib/treeInventory";

export function useTreeInventory() {
  const [state, setState] = useState<{ count: number; lastReward: TreeReward | null }>({
    count: 0,
    lastReward: null,
  });
  useEffect(() => subscribeInventory(setState), []);
  return state;
}
