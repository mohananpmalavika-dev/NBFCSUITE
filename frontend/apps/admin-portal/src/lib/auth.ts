/**
 * Authentication utilities
 */

import { apiClient } from './api-client'
import type { User, LoginRequest, LoginResponse } from '@/types'

const AUTH_TOKEN_KEY = 'auth_token'
const USER_KEY = 'user'
const TENANT_ID_KEY = 'tenant_id'

export class AuthService {
  /**
   * Login user
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login', credentials)
    
    if (response.success && response.data) {
      this.setToken(response.data.access_token)
      this.setUser(response.data.user)
      if (response.data.user.tenant_id) {
        this.setTenantId(response.data.user.tenant_id)
      }
      return response.data
    }
    
    throw new Error(response.error?.message || 'Login failed')
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      this.clearAuth()
    }
  }

  /**
   * Get current user
   */
  getUser(): User | null {
    if (typeof window === 'undefined') return null
    const userStr = localStorage.getItem(USER_KEY)
    if (!userStr) return null
    try {
      return JSON.parse(userStr)
    } catch {
      return null
    }
  }

  /**
   * Set user
   */
  setUser(user: User): void {
    if (typeof window === 'undefined') return
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  }

  /**
   * Get token
   */
  getToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem(AUTH_TOKEN_KEY)
  }

  /**
   * Set token
   */
  setToken(token: string): void {
    if (typeof window === 'undefined') return
    localStorage.setItem(AUTH_TOKEN_KEY, token)
    
    // Also set as cookie for middleware
    document.cookie = `auth_token=${token}; path=/; max-age=86400; SameSite=Lax`
    
    apiClient.setToken(token)
  }

  /**
   * Get tenant ID
   */
  getTenantId(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem(TENANT_ID_KEY)
  }

  /**
   * Set tenant ID
   */
  setTenantId(tenantId: string): void {
    if (typeof window === 'undefined') return
    localStorage.setItem(TENANT_ID_KEY, tenantId)
    apiClient.setTenantId(tenantId)
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getToken()
  }

  /**
   * Clear authentication
   */
  clearAuth(): void {
    if (typeof window === 'undefined') return
    localStorage.removeItem(AUTH_TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    localStorage.removeItem(TENANT_ID_KEY)
    
    // Also clear cookie
    document.cookie = 'auth_token=; path=/; max-age=0'
  }

  /**
   * Refresh token
   */
  async refreshToken(): Promise<void> {
    try {
      const response = await apiClient.post<{ access_token: string }>('/auth/refresh')
      if (response.success && response.data) {
        this.setToken(response.data.access_token)
      }
    } catch (error) {
      console.error('Token refresh failed:', error)
      this.clearAuth()
      throw error
    }
  }
}

export const authService = new AuthService()
