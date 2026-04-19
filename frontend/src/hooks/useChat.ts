/**
 * React hooks for chat functionality
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  intent?: string;
  created_at: string;
}

export interface StudySession {
  id: string;
  user_id: string;
  session_name: string;
  course_id?: string;
  course_name?: string;
  lesson_id?: string;
  lesson_title?: string;
  active_topic?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ChatResponse {
  session_id: string;
  message_id: string;
  response: string;
  response_depth: string;
  intent: string;
  energy_mode: string;
  sources: Array<{
    source_id: string;
    title: string;
    content: string;
  }>;
  quiz?: any;
  processing_time_ms: number;
  created_at: string;
}

// ============================================================================
// Create Session
// ============================================================================

export const useCreateSession = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: {
      session_name?: string;
      course_id?: string;
      course_name?: string;
      lesson_id?: string;
      lesson_title?: string;
      active_topic?: string;
    }) => {
      const response = await apiClient.post<StudySession>('/chat/session', data);
      if (response.error) throw new Error(response.error.detail);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
    },
  });
};

// ============================================================================
// Get Session
// ============================================================================

export const useGetSession = (sessionId?: string) => {
  return useQuery({
    queryKey: ['session', sessionId],
    queryFn: async () => {
      if (!sessionId) return null;
      const response = await apiClient.get<StudySession>(`/chat/session/${sessionId}`);
      if (response.error) throw new Error(response.error.detail);
      return response.data;
    },
    enabled: !!sessionId,
  });
};

// ============================================================================
// Get Session Messages
// ============================================================================

export const useGetSessionMessages = (sessionId?: string) => {
  return useQuery({
    queryKey: ['sessionMessages', sessionId],
    queryFn: async () => {
      if (!sessionId) return [];
      const response = await apiClient.get<ChatMessage[]>(
        `/chat/session/${sessionId}/messages`
      );
      if (response.error) throw new Error(response.error.detail);
      return response.data || [];
    },
    enabled: !!sessionId,
  });
};

// ============================================================================
// Send Message
// ============================================================================

export const useSendMessage = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: {
      session_id: string;
      message: string;
      intent?: string;
      include_sources?: boolean;
      include_quiz?: boolean;
    }) => {
      const response = await apiClient.post<ChatResponse>('/chat/send', data);
      if (response.error) throw new Error(response.error.detail);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ 
        queryKey: ['sessionMessages', data?.session_id] 
      });
      queryClient.invalidateQueries({ 
        queryKey: ['session', data?.session_id] 
      });
    },
  });
};

// ============================================================================
// End Session
// ============================================================================

export const useEndSession = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (sessionId: string) => {
      const response = await apiClient.post(`/chat/session/${sessionId}/end`);
      if (response.error) throw new Error(response.error.detail);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
    },
  });
};
