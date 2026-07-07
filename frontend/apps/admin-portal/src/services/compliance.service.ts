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
    return apiClient.get<PaginatedResponse<CRILCBorrower>>(
      '/compliance/crilc/borrowers',
      { params }
    )
  },

  async getBorrower(id: string) {
    return apiClient.get<CRILCBorrower>(`/compliance/crilc/borrowers/${id}`)
  },

  async createBorrower(data: CreateCRILCBorrowerRequest) {
    return apiClient.post<CRILCBorrower>('/compliance/crilc/borrowers', data)
  },

  async updateBorrower(id: string, data: UpdateCRILCBorrowerRequest) {
    return apiClient.put<CRILCBorrower>(`/compliance/crilc/borrowers/${id}`, data)
  },

  // ============================================================================
  // CRILC FACILITIES
  // ============================================================================

  async getBorrowerFacilities(borrowerId: string) {
    return apiClient.get<CRILCFacility[]>(
      `/compliance/crilc/borrowers/${borrowerId}/facilities`
    )
  },

  async createFacility(data: CreateCRILCFacilityRequest) {
    return apiClient.post<CRILCFacility>('/compliance/crilc/facilities', data)
  },

  async updateFacility(id: string, data: Partial<CreateCRILCFacilityRequest>) {
    return apiClient.put<CRILCFacility>(`/compliance/crilc/facilities/${id}`, data)
  },

  // ============================================================================
  // LARGE CREDIT IDENTIFICATION
  // ============================================================================

  async identifyLargeCredits(data: LargeCreditIdentificationRequest) {
    return apiClient.post<LargeCreditIdentificationResponse>(
      '/compliance/crilc/identify-large-credits',
      data
    )
  },

  // ============================================================================
  // CRILC QUARTERLY RETURNS
  // ============================================================================

  async getQuarterlyReturns(params?: PaginationParams) {
    return apiClient.get<PaginatedResponse<CRILCQuarterlyReturn>>(
      '/compliance/crilc/quarterly-returns',
      { params }
    )
  },

  async getQuarterlyReturn(id: string) {
    return apiClient.get<CRILCQuarterlyReturn>(
      `/compliance/crilc/quarterly-returns/${id}`
    )
  },

  async generateQuarterlyReturn(data: CreateCRILCQuarterlyReturnRequest) {
    return apiClient.post<CRILCQuarterlyReturn>(
      '/compliance/crilc/quarterly-returns',
      data
    )
  },

  async approveQuarterlyReturn(id: string) {
    return apiClient.post<CRILCQuarterlyReturn>(
      `/compliance/crilc/quarterly-returns/${id}/approve`
    )
  },

  async submitQuarterlyReturn(id: string, submissionReference: string) {
    return apiClient.post<CRILCQuarterlyReturn>(
      `/compliance/crilc/quarterly-returns/${id}/submit`,
      { submission_reference: submissionReference }
    )
  },

  // ============================================================================
  // SMA TRACKING
  // ============================================================================

  async calculateSMA(data: SMACalculationRequest) {
    return apiClient.post<SMACalculationResponse>(
      '/compliance/sma/calculate',
      data
    )
  },

  async getSMATracking(params?: PaginationParams & { as_on_date?: string; sma_status?: string }) {
    return apiClient.get<PaginatedResponse<SMATracking>>(
      '/compliance/sma/tracking',
      { params }
    )
  },

  async getSMATrackingById(id: string) {
    return apiClient.get<SMATracking>(`/compliance/sma/tracking/${id}`)
  },

  async getLoanSMAHistory(loanAccountId: string) {
    return apiClient.get<SMATracking[]>(
      `/compliance/sma/loan/${loanAccountId}/history`
    )
  },

  async getSMAStatusChanges(params?: PaginationParams & { loan_account_id?: string; borrower_id?: string }) {
    return apiClient.get<PaginatedResponse<SMAStatusHistory>>(
      '/compliance/sma/status-changes',
      { params }
    )
  },

  async getSMADashboard(asOnDate?: string) {
    return apiClient.get<SMADashboardStats>('/compliance/sma/dashboard', {
      params: { as_on_date: asOnDate },
    })
  },

  // ============================================================================
  // SMA QUARTERLY REPORTS
  // ============================================================================

  async generateSMAQuarterlyReport(data: CreateSMAQuarterlyReportRequest) {
    return apiClient.post<SMAQuarterlyReport>(
      '/compliance/sma/quarterly-reports',
      data
    )
  },

  // ============================================================================
  // COMPLIANCE ALERTS
  // ============================================================================

  async getAlerts(params?: PaginationParams & ComplianceAlertFilter) {
    return apiClient.get<PaginatedResponse<ComplianceAlert>>(
      '/compliance/alerts',
      { params }
    )
  },

  async acknowledgeAlert(id: string) {
    return apiClient.post(`/compliance/alerts/${id}/acknowledge`)
  },

  async resolveAlert(id: string, resolutionNotes: string) {
    return apiClient.post(`/compliance/alerts/${id}/resolve`, {
      resolution_notes: resolutionNotes,
    })
  },
}
