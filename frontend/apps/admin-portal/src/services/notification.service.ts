/**
 * Notification Service
 * API calls for notification management
 */

import { apiClient } from '@/lib/api-client'
import type { 
  Notification,
  NotificationTemplate,
  PaginatedResponse,
  PaginationParams 
} from '@/types'

export const notificationService = {
  // ============================================
  // Notifications
  // ============================================

  async getNotifications(params?: PaginationParams & { 
    status?: string
    channel?: string
    priority?: string 
  }) {
    return apiClient.get<PaginatedResponse<Notification>>('/notifications', { params })
  },

  async getNotification(id: string) {
    return apiClient.get<Notification>(`/notifications/${id}`)
  },

  async markAsRead(id: string) {
    return apiClient.post(`/notifications/${id}/mark-read`)
  },

  async markAllAsRead() {
    return apiClient.post('/notifications/mark-all-read')
  },

  async deleteNotification(id: string) {
    return apiClient.delete(`/notifications/${id}`)
  },

  // ============================================
  // Notification Templates
  // ============================================

  async getTemplates(params?: PaginationParams & { 
    channel?: string
    category?: string
    is_active?: boolean 
  }) {
    return apiClient.get<PaginatedResponse<NotificationTemplate>>('/notification-templates', { params })
  },

  async getTemplate(id: string) {
    return apiClient.get<NotificationTemplate>(`/notification-templates/${id}`)
  },

  async createTemplate(data: any) {
    return apiClient.post<NotificationTemplate>('/notification-templates', data)
  },

  async updateTemplate(id: string, data: any) {
    return apiClient.put<NotificationTemplate>(`/notification-templates/${id}`, data)
  },

  async deleteTemplate(id: string) {
    return apiClient.delete(`/notification-templates/${id}`)
  },

  // ============================================
  // Statistics
  // ============================================

  async getStatistics() {
    return apiClient.get('/notifications/statistics')
  },
}
