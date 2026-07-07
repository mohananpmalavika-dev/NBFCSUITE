/**
 * Risk Management Service
 * API calls for credit policies, risk-based pricing, exposure limits, risk ratings, and early warning systems
 */

import { apiClient } from '@/lib/api-client'
import type {
  CreditPolicy,
  RiskPricingRule,
  ExposureLimit,
  ExposureTransaction,
  RiskRating,
  EarlyWarningSignal,
  EarlyWarningAlert,
  PolicyEvaluationRequest,
  PolicyEvaluationResponse,
  PricingCalculationRequest,
  PricingCalculationResponse,
  RiskRatingStats,
  EarlyWarningAlertStats,
  RiskDashboardSummary,
  PaginatedResponse,
  PaginationParams
} from '@/types'

export const riskService = {
  // ============================================
  // Credit Policy Management
  // ============================================

  async getCreditPolicies(params?: PaginationParams & { is_active?: boolean; product_type?: string }) {
    const response = await apiClient.get<{ data: PaginatedResponse<CreditPolicy> }>('/risk/policies', { params })
    return response.data.data
  },

  async getCreditPolicy(id: number) {
    const response = await apiClient.get<{ data: CreditPolicy }>(`/risk/policies/${id}`)
    return response.data.data
  },

  async getCreditPolicyByCode(code: string) {
    const response = await apiClient.get<{ data: CreditPolicy }>(`/risk/policies/code/${code}`)
    return response.data.data
  },

  async createCreditPolicy(data: Partial<CreditPolicy>) {
    const response = await apiClient.post<{ data: CreditPolicy }>('/risk/policies', data)
    return response.data.data
  },

  async updateCreditPolicy(id: number, data: Partial<CreditPolicy>) {
    const response = await apiClient.put<{ data: CreditPolicy }>(`/risk/policies/${id}`, data)
    return response.data.data
  },

  async deleteCreditPolicy(id: number) {
    const response = await apiClient.delete<{ success: boolean }>(`/risk/policies/${id}`)
    return response.data.success
  },

  async evaluatePolicy(request: PolicyEvaluationRequest) {
    const response = await apiClient.post<{ data: PolicyEvaluationResponse }>('/risk/policies/evaluate', request)
    return response.data.data
  },

  // ============================================
  // Risk-Based Pricing
  // ============================================

  async getPricingRules(params?: PaginationParams & { policy_id?: number; is_active?: boolean }) {
    const response = await apiClient.get<{ data: PaginatedResponse<RiskPricingRule> }>('/risk/pricing-rules', { params })
    return response.data.data
  },

  async createPricingRule(data: Partial<RiskPricingRule>) {
    const response = await apiClient.post<{ data: RiskPricingRule }>('/risk/pricing-rules', data)
    return response.data.data
  },

  async calculatePricing(request: PricingCalculationRequest) {
    const response = await apiClient.post<{ data: PricingCalculationResponse }>('/risk/pricing-rules/calculate', request)
    return response.data.data
  },

  // ============================================
  // Exposure Limit Management
  // ============================================

  async getExposureLimits(params?: PaginationParams & { limit_type?: string; is_breached?: boolean }) {
    const response = await apiClient.get<{ data: PaginatedResponse<ExposureLimit> }>('/risk/exposure-limits', { params })
    return response.data.data
  },

  async getExposureLimit(id: number) {
    const response = await apiClient.get<{ data: ExposureLimit }>(`/risk/exposure-limits/${id}`)
    return response.data.data
  },

  async createExposureLimit(data: Partial<ExposureLimit>) {
    const response = await apiClient.post<{ data: ExposureLimit }>('/risk/exposure-limits', data)
    return response.data.data
  },

  async updateExposureLimit(id: number, data: Partial<ExposureLimit>) {
    const response = await apiClient.put<{ data: ExposureLimit }>(`/risk/exposure-limits/${id}`, data)
    return response.data.data
  },

  async utilizeExposure(id: number, data: {
    amount: number
    transaction_reference: string
    loan_application_id?: number
    loan_account_id?: number
    remarks?: string
  }) {
    const response = await apiClient.post<{ data: ExposureTransaction }>(`/risk/exposure-limits/${id}/utilize`, data)
    return response.data.data
  },

  async releaseExposure(id: number, data: {
    amount: number
    transaction_reference: string
    loan_application_id?: number
    loan_account_id?: number
    remarks?: string
  }) {
    const response = await apiClient.post<{ data: ExposureTransaction }>(`/risk/exposure-limits/${id}/release`, data)
    return response.data.data
  },

  // ============================================
  // Risk Rating Management
  // ============================================

  async getRiskRatings(params?: PaginationParams & { 
    customer_id?: string
    risk_grade?: string
    rating_type?: string
  }) {
    const response = await apiClient.get<{ data: PaginatedResponse<RiskRating> }>('/risk/ratings', { params })
    return response.data.data
  },

  async getLatestCustomerRating(customerId: string, ratingType: string = 'customer') {
    const response = await apiClient.get<{ data: RiskRating }>(
      `/risk/ratings/customer/${customerId}/latest`,
      { params: { rating_type: ratingType } }
    )
    return response.data.data
  },

  async createRiskRating(data: Partial<RiskRating>) {
    const response = await apiClient.post<{ data: RiskRating }>('/risk/ratings', data)
    return response.data.data
  },

  async overrideRiskRating(id: number, data: {
    new_risk_grade: string
    new_risk_score: number
    override_reason: string
  }) {
    const response = await apiClient.post<{ data: RiskRating }>(`/risk/ratings/${id}/override`, data)
    return response.data.data
  },

  async getRiskRatingStatistics() {
    const response = await apiClient.get<{ data: RiskRatingStats }>('/risk/ratings/statistics')
    return response.data.data
  },

  // ============================================
  // Early Warning Signals
  // ============================================

  async getEWSSignals(params?: PaginationParams & { category?: string; is_active?: boolean }) {
    const response = await apiClient.get<{ data: PaginatedResponse<EarlyWarningSignal> }>('/risk/ews/signals', { params })
    return response.data.data
  },

  async createEWSSignal(data: Partial<EarlyWarningSignal>) {
    const response = await apiClient.post<{ data: EarlyWarningSignal }>('/risk/ews/signals', data)
    return response.data.data
  },

  async updateEWSSignal(id: number, data: Partial<EarlyWarningSignal>) {
    const response = await apiClient.put<{ data: EarlyWarningSignal }>(`/risk/ews/signals/${id}`, data)
    return response.data.data
  },

  // ============================================
  // Early Warning Alerts
  // ============================================

  async getEWSAlerts(params?: PaginationParams & {
    status?: string
    severity?: string
    category?: string
    customer_id?: string
  }) {
    const response = await apiClient.get<{ data: PaginatedResponse<EarlyWarningAlert> }>('/risk/ews/alerts', { params })
    return response.data.data
  },

  async takeAlertAction(id: number, data: {
    action: 'acknowledge' | 'assign' | 'resolve' | 'escalate' | 'mark_false_positive'
    remarks?: string
    assigned_to?: string
    resolution_remarks?: string
  }) {
    const response = await apiClient.post<{ data: EarlyWarningAlert }>(`/risk/ews/alerts/${id}/action`, data)
    return response.data.data
  },

  async getEWSAlertStatistics() {
    const response = await apiClient.get<{ data: EarlyWarningAlertStats }>('/risk/ews/alerts/statistics')
    return response.data.data
  },

  async detectEarlyWarnings(loanAccountId: number) {
    const response = await apiClient.post<{ data: { alerts_created: number; alert_ids: number[] } }>(
      `/risk/ews/detect/${loanAccountId}`
    )
    return response.data.data
  },

  // ============================================
  // Dashboard & Analytics
  // ============================================

  async getDashboardSummary() {
    const response = await apiClient.get<{ data: RiskDashboardSummary }>('/risk/dashboard/summary')
    return response.data.data
  },
}
