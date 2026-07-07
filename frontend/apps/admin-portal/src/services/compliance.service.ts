/**
 * Compliance Service
 * API calls for CRILC & SMA Compliance Reporting
 */

import { apiClient } from '@/lib/api-client'
import type {
  CRILCBorrower,
  CreateCRILCBorrowerRequest,
  UpdateCRILCBorrowerRequest,
  CRILCFacility,
  CreateCRILCFacilityRequest,
  SMATracking,
  SMAStatusHistory,
  SMACalculationRequest,
  SMACalculationResponse,
  SMADashboardStats,
  CRILCQuarterlyReturn,
  CreateCRILCQuarterlyReturnRequest,
  SMAQuarterlyReport,
  CreateSMAQuarterlyReportRequest,
  ComplianceAlert,
  LargeCreditIdentificationRequest,
  LargeCreditIdentificationResponse,
  LargeCreditFilter,
  ComplianceAlertFilter,
  PaginatedResponse,
  PaginationParams,
} from '@/types'

export const complianceService = {
  // ============================================================================
  // CRILC BORROWERS
  // ============================================================================

  async getBorrowers(params?: PaginationParams & LargeCreditFilter) {
    const response = await apiClient.get<PaginatedResponse<CRILCBorrower>>(
      '/compliance/crilc/borrowers',
      { params }
    )
    return response.data
  },

  async getBorrower(id: string) {
    const response = await apiClient.get<CRILCBorrower>(`/compliance/crilc/borrowers/${id}`)
    return response.data
  },

  async createBorrower(data: CreateCRILCBorrowerRequest) {
    const response = await apiClient.post<CRILCBorrower>('/compliance/crilc/borrowers', data)
    return response.data
  },

  async updateBorrower(id: string, data: UpdateCRILCBorrowerRequest) {
    const response = await apiClient.put<CRILCBorrower>(`/compliance/crilc/borrowers/${id}`, data)
    return response.data
  },

  // ============================================================================
  // CRILC FACILITIES
  // ============================================================================

  async getBorrowerFacilities(borrowerId: string) {
    const response = await apiClient.get<CRILCFacility[]>(
      `/compliance/crilc/borrowers/${borrowerId}/facilities`
    )
    return response.data
  },

  async createFacility(data: CreateCRILCFacilityRequest) {
    const response = await apiClient.post<CRILCFacility>('/compliance/crilc/facilities', data)
    return response.data
  },

  async updateFacility(id: string, data: Partial<CreateCRILCFacilityRequest>) {
    const response = await apiClient.put<CRILCFacility>(`/compliance/crilc/facilities/${id}`, data)
    return response.data
  },

  // ============================================================================
  // LARGE CREDIT IDENTIFICATION
  // ============================================================================

  async identifyLargeCredits(data: LargeCreditIdentificationRequest) {
    const response = await apiClient.post<LargeCreditIdentificationResponse>(
      '/compliance/crilc/identify-large-credits',
      data
    )
    return response.data
  },

  // ============================================================================
  // CRILC QUARTERLY RETURNS
  // ============================================================================

  async getQuarterlyReturns(params?: PaginationParams) {
    const response = await apiClient.get<PaginatedResponse<CRILCQuarterlyReturn>>(
      '/compliance/crilc/quarterly-returns',
      { params }
    )
    return response.data
  },

  async getQuarterlyReturn(id: string) {
    const response = await apiClient.get<CRILCQuarterlyReturn>(
      `/compliance/crilc/quarterly-returns/${id}`
    )
    return response.data
  },

  async generateQuarterlyReturn(data: CreateCRILCQuarterlyReturnRequest) {
    const response = await apiClient.post<CRILCQuarterlyReturn>(
      '/compliance/crilc/quarterly-returns',
      data
    )
    return response.data
  },

  async approveQuarterlyReturn(id: string) {
    const response = await apiClient.post<CRILCQuarterlyReturn>(
      `/compliance/crilc/quarterly-returns/${id}/approve`
    )
    return response.data
  },

  async submitQuarterlyReturn(id: string, submissionReference: string) {
    const response = await apiClient.post<CRILCQuarterlyReturn>(
      `/compliance/crilc/quarterly-returns/${id}/submit`,
      { submission_reference: submissionReference }
    )
    return response.data
  },

  // ============================================================================
  // SMA TRACKING
  // ============================================================================

  async calculateSMA(data: SMACalculationRequest) {
    const response = await apiClient.post<SMACalculationResponse>(
      '/compliance/sma/calculate',
      data
    )
    return response.data
  },

  async getSMATracking(params?: PaginationParams & { as_on_date?: string; sma_status?: string }) {
    const response = await apiClient.get<PaginatedResponse<SMATracking>>(
      '/compliance/sma/tracking',
      { params }
    )
    return response.data
  },

  async getSMATrackingById(id: string) {
    const response = await apiClient.get<SMATracking>(`/compliance/sma/tracking/${id}`)
    return response.data
  },

  async getLoanSMAHistory(loanAccountId: string) {
    const response = await apiClient.get<SMATracking[]>(
      `/compliance/sma/loan/${loanAccountId}/history`
    )
    return response.data
  },

  async getSMAStatusChanges(params?: PaginationParams & { loan_account_id?: string; borrower_id?: string }) {
    const response = await apiClient.get<PaginatedResponse<SMAStatusHistory>>(
      '/compliance/sma/status-changes',
      { params }
    )
    return response.data
  },

  async getSMADashboard(asOnDate?: string) {
    const response = await apiClient.get<SMADashboardStats>('/compliance/sma/dashboard', {
      params: { as_on_date: asOnDate },
    })
    return response.data
  },

  // ============================================================================
  // SMA QUARTERLY REPORTS
  // ============================================================================

  async generateSMAQuarterlyReport(data: CreateSMAQuarterlyReportRequest) {
    const response = await apiClient.post<SMAQuarterlyReport>(
      '/compliance/sma/quarterly-reports',
      data
    )
    return response.data
  },

  // ============================================================================
  // COMPLIANCE ALERTS
  // ============================================================================

  async getAlerts(params?: PaginationParams & ComplianceAlertFilter) {
    const response = await apiClient.get<PaginatedResponse<ComplianceAlert>>(
      '/compliance/alerts',
      { params }
    )
    return response.data
  },

  async acknowledgeAlert(id: string) {
    const response = await apiClient.post(`/compliance/alerts/${id}/acknowledge`)
    return response.data
  },

  async resolveAlert(id: string, resolutionNotes: string) {
    const response = await apiClient.post(`/compliance/alerts/${id}/resolve`, {
      resolution_notes: resolutionNotes,
    })
    return response.data
  },
}
