/**
 * React hooks for readiness signals
 */

import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

export interface ReadinessSignal {
  workload_pressure_score: number;
  workload_pressure_band: string;
  study_stability_score: number;
  study_stability_band: string;
  performance_trend_score: number;
  performance_trend_band: string;
  behavioral_fatigue_score: number;
  behavioral_fatigue_band: string;
  recommended_intensity: string;
  suggested_session_minutes: number;
  energy_mode: string;
  support_tone: string;
  top_risk_flags: string[];
  reasoning_summary: string;
}

export interface ReadinessBehavioralSignals {
  tasks_due_3d: number;
  overdue_tasks: number;
  project_risk_level: string;
  study_sessions_last_7d: number;
  avg_session_completion_rate: number;
  avg_quiz_score_trend: number;
  late_night_activity_ratio: number;
  long_sessions_without_breaks: number;
}

// ============================================================================
// Update Readiness
// ============================================================================

export const useUpdateReadiness = () => {
  return useMutation({
    mutationFn: async (data: {
      session_id?: string;
      signals: ReadinessBehavioralSignals;
    }) => {
      const response = await apiClient.post<ReadinessSignal>(
        '/readiness/update',
        data
      );
      if (response.error) throw new Error(response.error.detail);
      return response.data;
    },
  });
};

// ============================================================================
// Get Current Readiness
// ============================================================================

export const useCurrentReadiness = () => {
  return useQuery({
    queryKey: ['currentReadiness'],
    queryFn: async () => {
      const response = await apiClient.get<ReadinessSignal>('/readiness/current');
      if (response.error) throw new Error(response.error.detail);
      return response.data;
    },
  });
};
