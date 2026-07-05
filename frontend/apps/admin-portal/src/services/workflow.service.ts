/**
 * Workflow Service
 * API calls for workflow management
 */

import { apiClient } from '@/lib/api-client'
import type { 
  WorkflowTemplate,
  WorkflowInstance,
  WorkflowTask,
  PaginatedResponse,
  PaginationParams 
} from '@/types'

export const workflowService = {
  // ============================================
  // Workflow Templates
  // ============================================

  async getTemplates(params?: PaginationParams) {
    return apiClient.get<PaginatedResponse<WorkflowTemplate>>('/workflow-templates', { params })
  },

  async getTemplate(id: string) {
    return apiClient.get<WorkflowTemplate>(`/workflow-templates/${id}`)
  },

  // ============================================
  // Workflow Instances
  // ============================================

  async getInstances(params?: PaginationParams & { status?: string; template_id?: string }) {
    return apiClient.get<PaginatedResponse<WorkflowInstance>>('/workflow-instances', { params })
  },

  async getInstance(id: string) {
    return apiClient.get<WorkflowInstance>(`/workflow-instances/${id}`)
  },

  async createInstance(data: { template_id: string; entity_type?: string; entity_id?: string }) {
    return apiClient.post<WorkflowInstance>('/workflow-instances', data)
  },

  async cancelInstance(id: string, reason?: string) {
    return apiClient.post(`/workflow-instances/${id}/cancel`, { reason })
  },

  // ============================================
  // Workflow Tasks
  // ============================================

  async getTasks(params?: PaginationParams & { 
    status?: string
    assigned_to?: string
    instance_id?: string 
  }) {
    return apiClient.get<PaginatedResponse<WorkflowTask>>('/workflow-tasks', { params })
  },

  async getTask(id: string) {
    return apiClient.get<WorkflowTask>(`/workflow-tasks/${id}`)
  },

  async getMyTasks(params?: PaginationParams & { status?: string }) {
    return apiClient.get<PaginatedResponse<WorkflowTask>>('/workflow-tasks/my-tasks', { params })
  },

  async claimTask(id: string) {
    return apiClient.post(`/workflow-tasks/${id}/claim`)
  },

  async completeTask(id: string, data: { result?: any; comments?: string }) {
    return apiClient.post(`/workflow-tasks/${id}/complete`, data)
  },

  async approveTask(id: string, comments?: string) {
    return apiClient.post(`/workflow-tasks/${id}/approve`, { comments })
  },

  async rejectTask(id: string, comments: string) {
    return apiClient.post(`/workflow-tasks/${id}/reject`, { comments })
  },
}
