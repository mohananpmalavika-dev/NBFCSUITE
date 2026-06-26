'use client';

import React, { createContext, useState, useCallback, ReactNode, useEffect } from 'react';
import { apiClient } from '@/lib/api';

interface User {
  id: string;
  username: string;
  email: string;
  roles: Array<string | { id: string; name: string; description?: string | null }>;
  organization_id?: string | null;
  zone_id?: string | null;
  region_id?: string | null;
  area_id?: string | null;
  branch_id?: string | null;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  isLoading: true,
  login: async () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    apiClient.clearToken();
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  }, []);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      apiClient.setToken(storedToken);
    }
    setIsLoading(false);
  }, []);

  useEffect(() => {
    if (token) {
      setIsLoading(true);
      apiClient.getMe()
        .then(response => {
          setUser(response.data);
          apiClient.setScope(response.data);
        })
        .catch(() => {
          logout();
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [token, logout]);

  const login = useCallback(async (username: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await apiClient.login(username, password);
      const { access_token, refresh_token } = response.data;

      setToken(access_token);
      apiClient.setToken(access_token);
      localStorage.setItem('token', access_token);
      if (refresh_token) {
        localStorage.setItem('refreshToken', refresh_token);
      }

      const userResponse = await apiClient.getMe();
      setUser(userResponse.data);
      apiClient.setScope(userResponse.data);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
