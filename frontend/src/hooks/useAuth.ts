/**
 * React hooks for authentication
 */

import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  academic_level: string;
  department?: string;
  learning_style: string;
  pace_preference: string;
  accessibility_needs: string[];
  strengths: string[];
  weak_topics: string[];
  is_active: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// ============================================================================
// Register
// ============================================================================

export const useRegister = () => {
  return useMutation({
    mutationFn: async (data: {
      email: string;
      username: string;
      full_name: string;
      password: string;
    }) => {
      const response = await apiClient.post('/auth/register', data);
      if (response.error) throw new Error(response.error.detail);
      return response.data;
    },
  });
};

// ============================================================================
// Login
// ============================================================================

export const useLogin = () => {
  return useMutation({
    mutationFn: async (data: { email: string; password: string }) => {
      const response = await apiClient.post<AuthTokens>('/auth/login', data);
      if (response.error) throw new Error(response.error.detail);
      
      if (response.data) {
        apiClient.setToken(response.data.access_token);
        localStorage.setItem('refresh_token', response.data.refresh_token);
      }
      
      return response.data;
    },
  });
};

// ============================================================================
// Get Current User
// ============================================================================

export const useCurrentUser = () => {
  return useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const response = await apiClient.get<User>('/user/me');
      if (response.error) throw new Error(response.error.detail);
      return response.data;
    },
    enabled: !!apiClient.getToken(),
  });
};

// ============================================================================
// Update User Profile
// ============================================================================

export const useUpdateUserProfile = () => {
  return useMutation({
    mutationFn: async (data: Partial<User>) => {
      const response = await apiClient.put<User>('/user/me', data);
      if (response.error) throw new Error(response.error.detail);
      return response.data;
    },
  });
};

// ============================================================================
// Logout
// ============================================================================

export const useLogout = () => {
  return useMutation({
    mutationFn: async () => {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await apiClient.post('/auth/logout', { refresh_token: refreshToken });
      }
      apiClient.setToken('');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },
  });
};
