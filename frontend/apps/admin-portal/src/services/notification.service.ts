/**
 * Notification Service
 * API calls for notification management, templates, preferences, and logs
 */

import { apiClient } from '@/lib/api-client'
import type { PaginatedResponse, PaginationParams } from '@/types'

// ============================================
// TYPE DEFINITIONS
// ============================================

export interface NotificationTemplate {
  id: number
  template_code: string
  template_name: string
  channel: string
  notification_type: string
  subject?: string
  body_template: string
  sms_template?: string
  is_active: boolean
  priority: string
  send_days_before?: number
  created_at: string
}

export interface NotificationPreference {
  id: number
  rent_due_reminder_enabled: boolean
  lease_expiry_alert_enabled: boolean
  payment_received_enabled: boolean
  maintenance_update_enabled: boolean
  utility_bill_due_enabled: boolean
  payment_overdue_enabled: boolean
  email_enabled: boolean
  sms_enabled: boolean
  email_address?: string
  phone_number?: string
}

export interface NotificationLog {
  id: number
  channel: string
  notification_type: string
  recipient_name?: string
  recipient_email?: string
  recipient_phone?: string
  subject?: string
  status: string
  sent_at?: string
  error_message?: string
  created_at: string
}

export interface NotificationStatistics {
  total_notifications: number
  by_status: Record<string, number>
  by_channel: Record<string, number>
  by_type: Record<string, number>
}

export const notificationService = {
  // ============================================
  // TEMPLATES
  // ============================================

  async getTemplates(params?: PaginationParams & {
    channel?: string
    is_active?: boolean
  }) {
    return apiClient.get<PaginatedResponse<NotificationTemplate>>('/notifications/templates', { params })
  },

  async getTemplate(id: number) {
    return apiClient.get<{ success: boolean; data: NotificationTemplate }>(`/notifications/templates/${id}`)
  },

  async createTemplate(data: any) {
    return apiClient.post('/notifications/templates', data)
  },

  async updateTemplate(id: number, data: any) {
    return apiClient.put(`/notifications/templates/${id}`, data)
  },

  // ============================================
  // PREFERENCES
  // ============================================

  async getPreferences() {
    return apiClient.get<{ success: boolean; data: NotificationPreference }>('/notifications/preferences')
  },

  async updatePreferences(data: Partial<NotificationPreference>) {
    return apiClient.put('/notifications/preferences', data)
  },

  // ============================================
  // LOGS
  // ============================================

  async getLogs(params?: PaginationParams & {
    channel?: string
    status?: string
    notification_type?: string
    start_date?: string
    end_date?: string
  }) {
    return apiClient.get<PaginatedResponse<NotificationLog>>('/notifications/logs', { params })
  },

  async getStatistics() {
    return apiClient.get<{ success: boolean; data: NotificationStatistics }>('/notifications/logs/statistics')
  },

  // ============================================
  // MANUAL SEND
  // ============================================

  async sendManualNotification(data: {
    recipient_email?: string
    recipient_phone?: string
    channel: string
    subject?: string
    message: string
    property_id?: number
    lease_id?: number
  }) {
    return apiClient.post('/notifications/send', data)
  },

  // ============================================
  // CHANNELS
  // ============================================

  async getChannels() {
    return apiClient.get<{ success: boolean; data: Array<{ value: string; label: string }> }>('/notifications/channels')
  },
}
