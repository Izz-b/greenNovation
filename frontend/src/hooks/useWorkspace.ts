/**
 * React hooks for workspace document analysis
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

export interface AnalysisDocument {
  document_id: string;
  title: string;
  summary: string;
  key_concepts: string[];
  generated_quiz?: any;
  created_at: string;
}

export interface DocumentSource {
  source_id: string;
  title: string;
  content: string;
}

export interface WorkspaceQueryResponse {
  document_id: string;
  query: string;
  response: string;
  sources: DocumentSource[];
  created_at: string;
}

// ============================================================================
// Analyze Document
// ============================================================================

export const useAnalyzeDocument = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: {
      title: string;
      content: string;
      document_type?: string;
    }) => {
      const response = await apiClient.post<AnalysisDocument>(
        '/workspace/analyze',
        data
      );
      if (response.error) throw new Error(response.error.detail);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
};

// ============================================================================
// Query Document
// ============================================================================

export const useQueryDocument = () => {
  return useMutation({
    mutationFn: async (data: {
      document_id: string;
      query: string;
      session_id?: string;
    }) => {
      const response = await apiClient.post<WorkspaceQueryResponse>(
        '/workspace/query',
        data
      );
      if (response.error) throw new Error(response.error.detail);
      return response.data;
    },
  });
};

// ============================================================================
// List Documents
// ============================================================================

export const useListDocuments = () => {
  return useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      const response = await apiClient.get<any>('/workspace/documents');
      if (response.error) throw new Error(response.error.detail);
      return response.data?.documents || [];
    },
  });
};

// ============================================================================
// Get Document
// ============================================================================

export const useGetDocument = (documentId?: string) => {
  return useQuery({
    queryKey: ['document', documentId],
    queryFn: async () => {
      if (!documentId) return null;
      const response = await apiClient.get<AnalysisDocument>(
        `/workspace/document/${documentId}`
      );
      if (response.error) throw new Error(response.error.detail);
      return response.data;
    },
    enabled: !!documentId,
  });
};
