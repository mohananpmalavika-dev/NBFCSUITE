/**
 * RBI Returns Service
 * API client for RBI Returns Automation
 */

import { apiClient } from '@/lib/api-client'
import type {
  RBIReturnMaster,
  CreateRBIReturnMasterRequest,
  NBS7Return,
  NBS7ReturnGenerateRequest,
  NBS7ReturnUpdateRequest,
  StatutoryReturn,
  CreateStatutoryReturnRequest,
  XBRLDocument,
  XBRLGenerateRequest,
  XBRLValidationResponse,
  ComplianceCalendarEvent,
  CreateComplianceCalendarRequest,
  UpdateComplianceCalendarRequest,
  CompleteCalendarEventRequest,
  RBIReturnsDashboardStats,
  ComplianceCalendarSummary,
  ReturnSubmissionHistory,
  RBIReturnsFilter,
  ComplianceCalendarFilter,
  PaginationParams,
  PaginatedResponse,
} from '@/types/rbi-returns.types'

export const rbiReturnsService = {
  // ============================================================================
  // RBI RETURN MASTER
  // ============================================================================

  async getReturnMasters(params?: {
    return_type?: string
    is_active?: boolean
  } & PaginationParams) {
    const response = await apiClient.get<RBIReturnMaster[]>('/rbi-returns/masters', { params })
    return response.data
  },

  async createReturnMaster(data: CreateRBIReturnMasterRequest) {
    const response = await apiClient.post<RBIReturnMaster>('/rbi-returns/masters', data)
    return response.data
  },

  // ============================================================================
  // NBS-7 RETURNS
  // ============================================================================

  async generateNBS7Return(request: NBS7ReturnGenerateRequest) {
    const response = await apiClient.post<NBS7Return>('/rbi-returns/nbs7/generate', request)
    return response.data
  },

  async listNBS7Returns(params?: {
    financial_year?: string
    quarter?: string
    status?: string
  } & PaginationParams) {
    const response = await apiClient.get<NBS7Return[]>('/rbi-returns/nbs7', { params })
    return response.data
  },

  async getNBS7Return(id: string) {
    const response = await apiClient.get<NBS7Return>(`/rbi-returns/nbs7/${id}`)
    return response.data
  },

  async updateNBS7Return(id: string, data: NBS7ReturnUpdateRequest) {
    const response = await apiClient.put<NBS7Return>(`/rbi-returns/nbs7/${id}`, data)
    return response.data
  },

  async approveNBS7Return(id: string) {
    const response = await apiClient.post<NBS7Return>(`/rbi-returns/nbs7/${id}/approve`)
    return response.data
  },

  async submitNBS7Return(id: string, submissionReference: string) {
    const response = await apiClient.post<NBS7Return>(`/rbi-returns/nbs7/${id}/submit`, {
      submission_reference: submissionReference,
    })
    return response.data
  },

  // ============================================================================
  // STATUTORY RETURNS
  // ============================================================================

  async createStatutoryReturn(data: CreateStatutoryReturnRequest) {
    const response = await apiClient.post<StatutoryReturn>('/rbi-returns/statutory', data)
    return response.data
  },

  async listStatutoryReturns(params?: {
    return_type?: string
    financial_year?: string
    status?: string
  } & PaginationParams) {
    const response = await apiClient.get<StatutoryReturn[]>('/rbi-returns/statutory', { params })
    return response.data
  },

  async getStatutoryReturn(id: string) {
    const response = await apiClient.get<StatutoryReturn>(`/rbi-returns/statutory/${id}`)
    return response.data
  },

  async validateStatutoryReturn(id: string) {
    const response = await apiClient.post<{
      is_valid: boolean
      errors: Array<{ field: string; message: string }>
      warnings: Array<{ field: string; message: string }>
    }>(`/rbi-returns/statutory/${id}/validate`)
    return response.data
  },

  async approveStatutoryReturn(id: string) {
    const response = await apiClient.post<StatutoryReturn>(`/rbi-returns/statutory/${id}/approve`)
    return response.data
  },

  async submitStatutoryReturn(id: string, submissionReference: string) {
    const response = await apiClient.post<StatutoryReturn>(`/rbi-returns/statutory/${id}/submit`, {
      submission_reference: submissionReference,
    })
    return response.data
  },

  // ============================================================================
  // XBRL DOCUMENTS
  // ============================================================================

  async generateXBRL(request: XBRLGenerateRequest) {
    const response = await apiClient.post<XBRLDocument>('/rbi-returns/xbrl/generate', request)
    return response.data
  },

  async getXBRLDocument(id: string) {
    const response = await apiClient.get<XBRLDocument>(`/rbi-returns/xbrl/${id}`)
    return response.data
  },

  async downloadXBRL(id: string) {
    const response = await apiClient.get(`/rbi-returns/xbrl/${id}/download`, {
      responseType: 'blob',
    })
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `xbrl-${id}.xml`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  },

  // ============================================================================
  // COMPLIANCE CALENDAR
  // ============================================================================

  async createCalendarEvent(data: CreateComplianceCalendarRequest) {
    const response = await apiClient.post<ComplianceCalendarEvent>('/rbi-returns/calendar', data)
    return response.data
  },

  async listCalendarEvents(params?: ComplianceCalendarFilter & PaginationParams) {
    const response = await apiClient.get<ComplianceCalendarEvent[]>('/rbi-returns/calendar', {
      params,
    })
    return response.data
  },

  async getCalendarEvent(id: string) {
    const response = await apiClient.get<ComplianceCalendarEvent>(`/rbi-returns/calendar/${id}`)
    return response.data
  },

  async updateCalendarEvent(id: string, data: UpdateComplianceCalendarRequest) {
    const response = await apiClient.put<ComplianceCalendarEvent>(
      `/rbi-returns/calendar/${id}`,
      data
    )
    return response.data
  },

  async completeCalendarEvent(id: string, request: CompleteCalendarEventRequest) {
    const response = await apiClient.post<ComplianceCalendarEvent>(
      `/rbi-returns/calendar/${id}/complete`,
      request
    )
    return response.data
  },

  async getUpcomingDeadlines(daysAhead: number = 30, limit: number = 10) {
    const response = await apiClient.get<ComplianceCalendarEvent[]>(
      '/rbi-returns/calendar/upcoming/deadlines',
      {
        params: { days_ahead: daysAhead, limit },
      }
    )
    return response.data
  },

  // ============================================================================
  // DASHBOARD & ANALYTICS
  // ============================================================================

  async getDashboardStats() {
    const response = await apiClient.get<RBIReturnsDashboardStats>('/rbi-returns/dashboard/stats')
    return response.data
  },

  async getCalendarSummary() {
    const response = await apiClient.get<ComplianceCalendarSummary>(
      '/rbi-returns/dashboard/calendar-summary'
    )
    return response.data
  },
}
