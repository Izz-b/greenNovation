import {
  useMutation,
  useQuery,
  useQueryClient,
  UseQueryResult,
  UseMutationResult,
} from "@tanstack/react-query";

/**
 * Types matching backend readiness.py schemas
 */

export interface Checkin {
  id: string;
  date: string;
  sleep: "bad" | "okay" | "great";
  focus: "low" | "medium" | "high";
  mood: "sad" | "neutral" | "happy";
  journal?: string | null;
  created_at: string;
}

export interface WeeklySummary {
  happy_pct: number;
  neutral_pct: number;
  sad_pct: number;
  avg_sleep: string;
  avg_focus: string;
  total_checkins: number;
}

export interface ReadinessHistory {
  checkins: Checkin[];
  summary: WeeklySummary;
}

export interface CheckinSubmitData {
  sleep: string;
  focus: string;
  mood: string;
  journal?: string;
}

/**
 * Submit today's well-being check-in
 *
 * Usage:
 * ```
 * const { mutate, isPending } = useSubmitCheckin();
 * mutate({ sleep: "great", focus: "high", mood: "happy" });
 * ```
 */
export const useSubmitCheckin = (): UseMutationResult<Checkin, Error, CheckinSubmitData> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CheckinSubmitData) => {
      const response = await fetch("/api/readiness/checkin", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to submit check-in");
      }

      return response.json() as Promise<Checkin>;
    },
    onSuccess: () => {
      // Invalidate queries so they refetch with new data
      queryClient.invalidateQueries({ queryKey: ["readiness", "today"] });
      queryClient.invalidateQueries({ queryKey: ["readiness", "history"] });
    },
  });
};

/**
 * Get today's check-in if already submitted
 *
 * Usage:
 * ```
 * const { data: todayCheckin, isLoading } = useReadinessToday();
 * if (!todayCheckin) return <CheckinForm />;
 * ```
 */
export const useReadinessToday = (): UseQueryResult<Checkin | null> => {
  return useQuery({
    queryKey: ["readiness", "today"],
    queryFn: async () => {
      const response = await fetch("/api/readiness/current");

      // 200 but null response means no check-in yet
      if (response.status === 204 || response.headers.get("content-length") === "0") {
        return null;
      }

      if (!response.ok) {
        return null;
      }

      const data = await response.json();
      return data as Checkin | null;
    },
    // Refetch every 5 minutes to see if new check-in submitted
    staleTime: 5 * 60 * 1000,
  });
};

/**
 * Get historical check-ins and weekly summary
 *
 * Usage:
 * ```
 * const { data, isLoading } = useReadinessHistory(7);
 * data?.checkins.map(c => <CheckinCard key={c.id} checkin={c} />)
 * ```
 */
export const useReadinessHistory = (days: number = 7): UseQueryResult<ReadinessHistory> => {
  return useQuery({
    queryKey: ["readiness", "history", days],
    queryFn: async () => {
      const response = await fetch(`/api/readiness/history?days=${days}`);

      if (!response.ok) {
        throw new Error("Failed to fetch readiness history");
      }

      const data = await response.json();

      return {
        checkins: data.data as Checkin[],
        summary: data.week_summary as WeeklySummary,
      };
    },
    // Keep cache for 10 minutes
    staleTime: 10 * 60 * 1000,
  });
};
