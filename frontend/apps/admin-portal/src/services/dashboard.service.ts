/**
 * Dashboard Service
 * API calls for dashboard data
 */

import { apiClient } from '@/lib/api-client'
import type { DashboardStats, RecentActivity } from '@/types'

export const dashboardService = {
  /**
   * Get dashboard statistics
   */
  async getStats() {
    return apiClient.get<DashboardStats>('/dashboard/stats')
  },

  /**
   * Get recent activities
   */
  async getRecentActivities(limit: number = 10) {
    return apiClient.get<RecentActivity[]>('/dashboard/activities', {
      params: { limit }
    })
  },

  /**
   * Get loan portfolio summary
   */
  async getLoanPortfolio() {
    return apiClient.get('/dashboard/loan-portfolio')
  },

  /**
   * Get collection summary
   */
  async getCollectionSummary() {
    return apiClient.get('/dashboard/collection-summary')
  },

  /**
   * Get deposit summary
   */
  async getDepositSummary() {
    return apiClient.get('/dashboard/deposit-summary')
  },
}
