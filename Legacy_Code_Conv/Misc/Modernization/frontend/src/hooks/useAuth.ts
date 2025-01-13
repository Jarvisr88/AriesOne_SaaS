/**
 * Authentication hook for managing user session
 */
import { useCallback, useEffect, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { User } from '../types';

interface LoginCredentials {
  email: string;
  password: string;
}

interface AuthResponse {
  user: User;
  token: string;
}

const API_URL = process.env.REACT_APP_API_URL || '';

export const useAuth = () => {
  const queryClient = useQueryClient();
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('token')
  );

  // Configure axios interceptor for token
  useEffect(() => {
    const interceptor = axios.interceptors.request.use(
      (config) => {
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    return () => {
      axios.interceptors.request.eject(interceptor);
    };
  }, [token]);

  // Get current user
  const {
    data: user,
    isLoading,
    error
  } = useQuery<User>(
    ['user'],
    async () => {
      if (!token) return null;
      const { data } = await axios.get(
        `${API_URL}/auth/me`
      );
      return data;
    },
    {
      enabled: !!token,
      retry: false,
      onError: () => {
        // Clear invalid token
        localStorage.removeItem('token');
        setToken(null);
      }
    }
  );

  // Login mutation
  const loginMutation = useMutation<
    AuthResponse,
    Error,
    LoginCredentials
  >(
    async (credentials) => {
      const { data } = await axios.post(
        `${API_URL}/auth/login`,
        credentials
      );
      return data;
    },
    {
      onSuccess: (data) => {
        localStorage.setItem('token', data.token);
        setToken(data.token);
        queryClient.setQueryData(['user'], data.user);
      }
    }
  );

  // Logout
  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setToken(null);
    queryClient.setQueryData(['user'], null);
    queryClient.clear();
  }, [queryClient]);

  // Check if user has required roles
  const hasRoles = useCallback(
    (requiredRoles: string[]) => {
      if (!user || !user.roles) return false;
      return requiredRoles.some(role =>
        user.roles.includes(role)
      );
    },
    [user]
  );

  return {
    user,
    token,
    isLoading,
    error,
    login: loginMutation.mutate,
    logout,
    hasRoles,
    isAuthenticated: !!user
  };
};
