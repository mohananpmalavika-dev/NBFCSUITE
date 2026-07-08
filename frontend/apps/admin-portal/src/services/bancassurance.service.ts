/**
 * Bancassurance Service
 * API calls for Insurance & Bancassurance module
 * Handles policies, premiums, claims, and commissions
 */

import { apiClient } from '@/lib/api-client'
import type { PaginatedResponse, PaginationParams } from '@/types'

// ============================================
// Types & Interfaces
// ============================================

export interface InsurancePolicy {
  id: string
  tenant_id: string
  policy_number: string
  policy_type: 'life' | 'health' | 'general' | 'motor' | 'endowment' | 'term' | 'ulip' | 'pension'
  policy_status: 'draft' | 'active' | 'lapsed' | 'surrendered' | 'matured' | 'cancelled'
  
  // Customer & Insured
  customer_id: string
  customer_name: string
  insured_name: string
  insured_dob: string
  insured_age: number
  insured_gender?: string
  
  // Insurance Provider
  insurance_company: string
  insurance_company_code?: string
  product_name: string
  product_code?: string
  
  // Policy Details
  sum_assured: number
  policy_term_years: number
  premium_paying_term_years: number
  premium_amount: number
  premium_frequency: 'monthly' | 'quarterly' | 'half_yearly' | 'annually' | 'single'
  premium_mode?: string
  
  // Dates
  policy_start_date: string
  policy_end_date: string
  first_premium_date: string
  next_premium_due_date?: string
  maturity_date?: string
  
  // Agent/Channel
  agent_id?: string
  agent_name?: string
  agent_code?: string
  channel: string
  branch_id?: string
  branch_name?: string
  
  // Nominee
  nominee_name?: string
  nominee_relationship?: string
  nominee_dob?: string
  nominee_percentage?: number
  
  // Financial
  total_premium_paid: number
  total_premium_due: number
  outstanding_premium: number
  premiums_paid_count: number
  premiums_due_count: number
  surrender_value?: number
  maturity_value?: number
  
  // Status
  is_active: boolean
  is_lapsed: boolean
  lapsed_date?: string
  grace_period_days: number
  
  // Additional
  documents?: any[]
  remarks?: string
  rider_details?: any[]
  
  created_at: string
  updated_at: string
}

export interface InsurancePremium {
  id: string
  tenant_id: string
  policy_id: string
  policy_number: string
  premium_number: string
  premium_amount: number
  premium_due_date: string
  premium_frequency: string
  installment_number: number
  premium_status: 'due' | 'paid' | 'overdue' | 'waived' | 'cancelled'
  
  // Payment
  payment_date?: string
  payment_amount?: number
  payment_method?: string
  payment_reference?: string
  transaction_id?: string
  receipt_number?: string
  
  // Late Payment
  grace_period_end_date?: string
  late_fee?: number
  late_days?: number
  
  // Discounts/Waivers
  discount_amount?: number
  discount_reason?: string
  waived_amount?: number
  waived_reason?: string
  
  // Collection
  collected_by?: string
  collected_by_name?: string
  collection_branch?: string
  
  remarks?: string
  created_at: string
  updated_at: string
}

export interface InsuranceClaim {
  id: string
  tenant_id: string
  policy_id: string
  policy_number: string
  claim_number: string
  claim_type: 'death' | 'maturity' | 'surrender' | 'health' | 'accident' | 'damage' | 'theft' | 'other'
  claim_status: 'registered' | 'under_review' | 'documents_pending' | 'assessment_complete' | 'approved' | 'rejected' | 'settled' | 'cancelled'
  
  // Claim Details
  claim_amount: number
  claimed_date: string
  incident_date: string
  incident_description: string
  incident_location?: string
  
  // Claimant
  claimant_name: string
  claimant_relationship: string
  claimant_contact?: string
  claimant_address?: string
  
  // Assessment
  assessed_by?: string
  assessed_by_name?: string
  assessment_date?: string
  assessed_amount?: number
  assessment_remarks?: string
  
  // Approval
  approved_by?: string
  approved_by_name?: string
  approval_date?: string
  approved_amount?: number
  approval_remarks?: string
  
  // Rejection
  rejection_reason?: string
  rejection_date?: string
  
  // Settlement
  settlement_date?: string
  settlement_amount?: number
  settlement_method?: string
  settlement_reference?: string
  settlement_remarks?: string
  
  // Documents
  documents_submitted?: any[]
  documents_verified: boolean
  
  // Investigation
  investigation_required: boolean
  investigation_status?: string
  
  // Financial
  deductions?: number
  net_payable?: number
  processing_days?: number
  
  remarks?: string
  created_at: string
  updated_at: string
}

export interface InsuranceCommission {
  id: string
  tenant_id: string
  policy_id: string
  policy_number: string
  commission_number: string
  commission_status: 'pending' | 'calculated' | 'approved' | 'paid' | 'cancelled'
  
  // Agent
  agent_id: string
  agent_name: string
  agent_code?: string
  agent_type?: string
  
  // Commission
  commission_type: 'first_year' | 'renewal' | 'performance'
  base_amount: number
  commission_rate: number
  commission_amount: number
  commission_period?: string
  
  // Premium Reference
  premium_id?: string
  premium_number?: string
  
  // Approval
  approved_by?: string
  approved_by_name?: string
  approval_date?: string
  
  // Payment
  payment_date?: string
  payment_method?: string
  payment_reference?: string
  paid_amount?: number
  
  // Deductions
  tds_amount?: number
  tds_percentage?: number
  other_deductions?: number
  net_payable?: number
  
  // Performance
  bonus_amount?: number
  penalty_amount?: number
  
  calculation_date: string
  remarks?: string
  created_at: string
  updated_at: string
}

export interface PolicyStatistics {
  total_policies: number
  active_policies: number
  lapsed_policies: number
  matured_policies: number
  total_sum_assured: number
  total_premium_collected: number
  outstanding_premium: number
  policies_by_type: Record<string, number>
  policies_by_status: Record<string, number>
}

export interface PremiumStatistics {
  total_premiums: number
  paid_premiums: number
  due_premiums: number
  overdue_premiums: number
  total_premium_amount: number
  total_collected: number
  total_outstanding: number
  collection_rate: number
}

export interface ClaimStatistics {
  total_claims: number
  claims_by_status: Record<string, number>
  claims_by_type: Record<string, number>
  total_claimed_amount: number
  total_assessed_amount: number
  total_approved_amount: number
  total_settled_amount: number
  average_processing_days?: number
  settlement_rate: number
}

export interface CommissionStatistics {
  total_commissions: number
  pending_commissions: number
  approved_commissions: number
  paid_commissions: number
  total_commission_amount: number
  total_paid_amount: number
  total_outstanding: number
  commissions_by_type: Record<string, number>
  commissions_by_agent: Array<{
    agent_id: string
    agent_name: string
    total_commission: number
  }>
}

// ============================================
// API Service
// ============================================

export const bancassuranceService = {
  // ============================================
  // POLICIES
  // ============================================

  async createPolicy(data: Partial<InsurancePolicy>) {
    return apiClient.post<{ success: boolean; data: InsurancePolicy }>('/insurance/policies', data)
  },

  async getPolicies(params?: PaginationParams & {
    policy_type?: string
    policy_status?: string
    customer_id?: string
    agent_id?: string
    is_active?: boolean
  }) {
    return apiClient.get<{ success: boolean; data: { policies: InsurancePolicy[]; total: number } }>(
      '/insurance/policies',
      { params }
    )
  },

  async getPolicy(id: string) {
    return apiClient.get<{ success: boolean; data: InsurancePolicy }>(`/insurance/policies/${id}`)
  },

  async getPolicyByNumber(policyNumber: string) {
    return apiClient.get<{ success: boolean; data: InsurancePolicy }>(
      `/insurance/policies/number/${policyNumber}`
    )
  },

  async updatePolicy(id: string, data: Partial<InsurancePolicy>) {
    return apiClient.patch<{ success: boolean; data: InsurancePolicy }>(
      `/insurance/policies/${id}`,
      data
    )
  },

  async deletePolicy(id: string) {
    return apiClient.delete<{ success: boolean; message: string }>(`/insurance/policies/${id}`)
  },

  async activatePolicy(id: string) {
    return apiClient.post<{ success: boolean; data: InsurancePolicy }>(
      `/insurance/policies/${id}/activate`
    )
  },

  async lapsePolicy(id: string, reason?: string) {
    return apiClient.post<{ success: boolean; data: InsurancePolicy }>(
      `/insurance/policies/${id}/lapse`,
      null,
      { params: { reason } }
    )
  },

  async revivePolicy(id: string, arrearAmount: number) {
    return apiClient.post<{ success: boolean; data: InsurancePolicy }>(
      `/insurance/policies/${id}/revive`,
      null,
      { params: { arrear_amount: arrearAmount } }
    )
  },

  async surrenderPolicy(id: string) {
    return apiClient.post<{ success: boolean; data: InsurancePolicy }>(
      `/insurance/policies/${id}/surrender`
    )
  },

  async maturePolicy(id: string) {
    return apiClient.post<{ success: boolean; data: InsurancePolicy }>(
      `/insurance/policies/${id}/mature`
    )
  },

  async getPolicyStatistics() {
    return apiClient.get<{ success: boolean; data: PolicyStatistics }>(
      '/insurance/policies/stats/summary'
    )
  },

  // ============================================
  // PREMIUMS
  // ============================================

  async getPremiums(params?: PaginationParams & {
    policy_id?: string
    premium_status?: string
    from_due_date?: string
    to_due_date?: string
  }) {
    return apiClient.get<{ success: boolean; data: { premiums: InsurancePremium[]; total: number } }>(
      '/insurance/premiums',
      { params }
    )
  },

  async getPremium(id: string) {
    return apiClient.get<{ success: boolean; data: InsurancePremium }>(`/insurance/premiums/${id}`)
  },

  async getPremiumByNumber(premiumNumber: string) {
    return apiClient.get<{ success: boolean; data: InsurancePremium }>(
      `/insurance/premiums/number/${premiumNumber}`
    )
  },

  async recordPremiumPayment(id: string, data: {
    payment_date: string
    payment_amount: number
    payment_method: string
    payment_reference?: string
    transaction_id?: string
    receipt_number?: string
    collected_by_name?: string
    collection_branch?: string
    late_fee?: number
    remarks?: string
  }) {
    return apiClient.post<{ success: boolean; data: InsurancePremium }>(
      `/insurance/premiums/${id}/pay`,
      data
    )
  },

  async waivePremium(id: string, data: {
    waived_amount: number
    waived_reason: string
    remarks?: string
  }) {
    return apiClient.post<{ success: boolean; data: InsurancePremium }>(
      `/insurance/premiums/${id}/waive`,
      null,
      { params: data }
    )
  },

  async applyDiscount(id: string, data: {
    discount_amount: number
    discount_reason: string
  }) {
    return apiClient.post<{ success: boolean; data: InsurancePremium }>(
      `/insurance/premiums/${id}/discount`,
      null,
      { params: data }
    )
  },

  async getDuePremiums(params?: { policy_id?: string; include_overdue?: boolean }) {
    return apiClient.get<{ success: boolean; data: { premiums: InsurancePremium[]; total: number } }>(
      '/insurance/premiums/status/due',
      { params }
    )
  },

  async getOverduePremiums(params?: { policy_id?: string }) {
    return apiClient.get<{ success: boolean; data: { premiums: InsurancePremium[]; total: number } }>(
      '/insurance/premiums/status/overdue',
      { params }
    )
  },

  async markOverduePremiums() {
    return apiClient.post<{ success: boolean; data: { count: number } }>(
      '/insurance/premiums/batch/mark-overdue'
    )
  },

  async generatePremiums(data: {
    generation_date: string
    frequency: string
  }) {
    return apiClient.post<{ success: boolean; data: any }>(
      '/insurance/premiums/batch/generate',
      data
    )
  },

  async getPremiumStatistics(policyId?: string) {
    return apiClient.get<{ success: boolean; data: PremiumStatistics }>(
      '/insurance/premiums/stats/summary',
      { params: { policy_id: policyId } }
    )
  },

  // ============================================
  // CLAIMS
  // ============================================

  async createClaim(data: Partial<InsuranceClaim>) {
    return apiClient.post<{ success: boolean; data: InsuranceClaim }>('/insurance/claims', data)
  },

  async getClaims(params?: PaginationParams & {
    policy_id?: string
    claim_type?: string
    claim_status?: string
    from_claimed_date?: string
    to_claimed_date?: string
  }) {
    return apiClient.get<{ success: boolean; data: { claims: InsuranceClaim[]; total: number } }>(
      '/insurance/claims',
      { params }
    )
  },

  async getClaim(id: string) {
    return apiClient.get<{ success: boolean; data: InsuranceClaim }>(`/insurance/claims/${id}`)
  },

  async getClaimByNumber(claimNumber: string) {
    return apiClient.get<{ success: boolean; data: InsuranceClaim }>(
      `/insurance/claims/number/${claimNumber}`
    )
  },

  async markClaimUnderReview(id: string, remarks?: string) {
    return apiClient.post<{ success: boolean; data: InsuranceClaim }>(
      `/insurance/claims/${id}/review`,
      null,
      { params: { remarks } }
    )
  },

  async markDocumentsPending(id: string, remarks?: string) {
    return apiClient.post<{ success: boolean; data: InsuranceClaim }>(
      `/insurance/claims/${id}/documents-pending`,
      null,
      { params: { remarks } }
    )
  },

  async assessClaim(id: string, data: {
    assessed_amount: number
    assessment_remarks?: string
    documents_verified?: boolean
    deductions?: number
    investigation_status?: string
    investigation_remarks?: string
  }) {
    return apiClient.post<{ success: boolean; data: InsuranceClaim }>(
      `/insurance/claims/${id}/assess`,
      data
    )
  },

  async approveClaim(id: string, data: {
    approved_amount: number
    approval_remarks?: string
    target_settlement_date?: string
  }) {
    return apiClient.post<{ success: boolean; data: InsuranceClaim }>(
      `/insurance/claims/${id}/approve`,
      data
    )
  },

  async rejectClaim(id: string, data: {
    rejection_reason: string
  }) {
    return apiClient.post<{ success: boolean; data: InsuranceClaim }>(
      `/insurance/claims/${id}/reject`,
      data
    )
  },

  async settleClaim(id: string, data: {
    settlement_amount: number
    settlement_method: string
    settlement_reference?: string
    settlement_remarks?: string
  }) {
    return apiClient.post<{ success: boolean; data: InsuranceClaim }>(
      `/insurance/claims/${id}/settle`,
      data
    )
  },

  async getClaimStatistics(policyId?: string) {
    return apiClient.get<{ success: boolean; data: ClaimStatistics }>(
      '/insurance/claims/stats/summary',
      { params: { policy_id: policyId } }
    )
  },

  // ============================================
  // COMMISSIONS
  // ============================================

  async createCommission(data: Partial<InsuranceCommission>) {
    return apiClient.post<{ success: boolean; data: InsuranceCommission }>(
      '/insurance/commissions',
      data
    )
  },

  async getCommissions(params?: PaginationParams & {
    policy_id?: string
    agent_id?: string
    commission_status?: string
    commission_type?: string
  }) {
    return apiClient.get<{ success: boolean; data: { commissions: InsuranceCommission[]; total: number } }>(
      '/insurance/commissions',
      { params }
    )
  },

  async getCommission(id: string) {
    return apiClient.get<{ success: boolean; data: InsuranceCommission }>(
      `/insurance/commissions/${id}`
    )
  },

  async getCommissionByNumber(commissionNumber: string) {
    return apiClient.get<{ success: boolean; data: InsuranceCommission }>(
      `/insurance/commissions/number/${commissionNumber}`
    )
  },

  async approveCommission(id: string, data: {
    approved_by: string
    approval_remarks?: string
  }) {
    return apiClient.post<{ success: boolean; data: InsuranceCommission }>(
      `/insurance/commissions/${id}/approve`,
      data
    )
  },

  async payCommission(id: string, data: {
    payment_method: string
    payment_reference: string
    paid_amount: number
    payment_remarks?: string
  }) {
    return apiClient.post<{ success: boolean; data: InsuranceCommission }>(
      `/insurance/commissions/${id}/pay`,
      data
    )
  },

  async cancelCommission(id: string, reason?: string) {
    return apiClient.post<{ success: boolean; data: InsuranceCommission }>(
      `/insurance/commissions/${id}/cancel`,
      null,
      { params: { reason } }
    )
  },

  async calculateFirstYearCommission(policyId: string, agentId: string) {
    return apiClient.post<{ success: boolean; data: InsuranceCommission }>(
      '/insurance/commissions/calculate/first-year',
      null,
      { params: { policy_id: policyId, agent_id: agentId } }
    )
  },

  async calculateRenewalCommission(premiumId: string) {
    return apiClient.post<{ success: boolean; data: InsuranceCommission }>(
      '/insurance/commissions/calculate/renewal',
      null,
      { params: { premium_id: premiumId } }
    )
  },

  async batchCalculateCommissions(data: {
    calculation_period: string
    commission_type: string
    agent_ids?: string[]
  }) {
    return apiClient.post<{ success: boolean; data: any }>(
      '/insurance/commissions/batch/calculate',
      data
    )
  },

  async getCommissionStatistics(agentId?: string) {
    return apiClient.get<{ success: boolean; data: CommissionStatistics }>(
      '/insurance/commissions/stats/summary',
      { params: { agent_id: agentId } }
    )
  },
}
