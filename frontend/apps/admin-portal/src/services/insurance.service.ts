/**
 * Loan Insurance Service
 * API calls for loan insurance tracking and claims management
 */

import { apiClient } from '@/lib/api-client'
import type { PaginatedResponse, PaginationParams } from '@/types'

export interface InsurancePolicy {
  id: number
  loan_account_id: number
  insurance_type: 'life' | 'credit_protection' | 'asset' | 'health' | 'property' | 'vehicle_comprehensive' | 'other'
  insurance_provider: string
  policy_number: string
  status: 'active' | 'expired' | 'cancelled' | 'lapsed' | 'pending_renewal' | 'pending_activation'
  
  // Coverage details
  sum_assured: number
  premium_amount: number
  premium_frequency: 'monthly' | 'quarterly' | 'half_yearly' | 'yearly' | 'one_time'
  
  // Policy period
  policy_start_date: string
  policy_end_date: string
  
  // Beneficiary
  nominee_name?: string
  nominee_relationship?: string
  nominee_contact?: string
  
  // Policy terms
  is_mandatory: boolean
  is_bundled: boolean
  cover_percentage?: number
  
  // Renewal
  last_renewal_date?: string
  next_renewal_date?: string
  renewal_reminder_sent: boolean
  
  // Additional
  policy_document_url?: string
  agent_name?: string
  agent_contact?: string
  remarks?: string
  
  created_at: string
  updated_at: string
}

export interface CreatePolicyRequest {
  loan_account_id: number
  insurance_type: string
  insurance_provider: string
  policy_number: string
  sum_assured: number
  premium_amount: number
  premium_frequency: string
  policy_start_date: string
  policy_end_date: string
  nominee_name?: string
  nominee_relationship?: string
  nominee_contact?: string
  is_mandatory?: boolean
  is_bundled?: boolean
  cover_percentage?: number
  policy_document_url?: string
  agent_name?: string
  agent_contact?: string
  remarks?: string
}

export interface RenewPolicyRequest {
  policy_number: string
  policy_start_date: string
  policy_end_date: string
  sum_assured: number
  premium_amount: number
  policy_document_url?: string
  renewal_remarks?: string
}

export interface CancelPolicyRequest {
  cancellation_reason: string
  cancellation_date: string
  refund_amount?: number
}

export interface PremiumPayment {
  id: number
  insurance_policy_id: number
  due_date: string
  premium_amount: number
  payment_frequency: string
  payment_status: 'paid' | 'pending' | 'overdue' | 'failed' | 'waived'
  payment_date?: string
  amount_paid?: number
  payment_method?: string
  transaction_reference?: string
  receipt_url?: string
  is_overdue: boolean
  overdue_days?: number
  is_waived: boolean
  waiver_reason?: string
  remarks?: string
  created_at: string
}

export interface CreatePremiumPaymentRequest {
  insurance_policy_id: number
  due_date: string
  premium_amount: number
  payment_frequency: string
}

export interface UpdatePremiumPaymentRequest {
  payment_date: string
  amount_paid: number
  payment_method: string
  transaction_reference?: string
  receipt_url?: string
  remarks?: string
}

export interface InsuranceClaim {
  id: number
  insurance_policy_id: number
  loan_account_id: number
  claim_number: string
  claim_type: 'death' | 'disability' | 'critical_illness' | 'job_loss' | 'accident' | 'asset_damage' | 'theft' | 'natural_calamity' | 'other'
  claim_status: 'draft' | 'submitted' | 'under_review' | 'approved' | 'rejected' | 'paid' | 'partially_paid' | 'cancelled'
  
  // Claim details
  claim_amount: number
  incident_date: string
  incident_description: string
  incident_location?: string
  
  // Supporting documents
  supporting_documents: string[]
  police_report_number?: string
  medical_report_reference?: string
  
  // Claimant
  claimant_name: string
  claimant_relationship: string
  claimant_contact: string
  claimant_address?: string
  
  // Review
  approved_amount?: number
  rejection_reason?: string
  review_remarks?: string
  surveyor_name?: string
  surveyor_report_url?: string
  
  // Payment
  payment_date?: string
  amount_paid?: number
  payment_method?: string
  payment_reference?: string
  payee_name?: string
  bank_name?: string
  
  // Workflow
  submitted_at?: string
  reviewed_at?: string
  reviewed_by?: number
  paid_at?: string
  
  remarks?: string
  created_at: string
}

export interface CreateClaimRequest {
  insurance_policy_id: number
  loan_account_id: number
  claim_type: string
  claim_amount: number
  incident_date: string
  incident_description: string
  incident_location?: string
  supporting_documents: string[]
  police_report_number?: string
  medical_report_reference?: string
  claimant_name: string
  claimant_relationship: string
  claimant_contact: string
  claimant_address?: string
  remarks?: string
}

export interface ReviewClaimRequest {
  status: string
  approved_amount?: number
  rejection_reason?: string
  review_remarks: string
  surveyor_name?: string
  surveyor_report_url?: string
}

export interface ClaimPaymentRequest {
  payment_date: string
  amount_paid: number
  payment_method: string
  payment_reference: string
  payee_name: string
  bank_name?: string
  remarks?: string
}

export interface InsuranceStatistics {
  total_policies: number
  active_policies: number
  expired_policies: number
  cancelled_policies: number
  by_type: Record<string, number>
  total_sum_assured: number
  total_premium_collected: number
  average_coverage_per_loan: number
  expiring_30_days: number
  expiring_60_days: number
  expiring_90_days: number
  total_premiums_due: number
  total_premiums_overdue: number
  overdue_premium_count: number
  total_claims: number
  pending_claims: number
  approved_claims: number
  rejected_claims: number
  total_claim_amount: number
  total_paid_amount: number
  claim_settlement_ratio: number
}

export const insuranceService = {
  // ============================================
  // Insurance Policies
  // ============================================

  async createPolicy(data: CreatePolicyRequest) {
    return apiClient.post<InsurancePolicy>('/loan-insurance/policies', data)
  },

  async getPolicy(id: number) {
    return apiClient.get<InsurancePolicy>(`/loan-insurance/policies/${id}`)
  },

  async getPolicies(params?: PaginationParams & {
    loan_account_id?: number
    insurance_type?: string
    status?: string
    is_mandatory?: boolean
    expiring_before?: string
  }) {
    return apiClient.get<PaginatedResponse<InsurancePolicy>>('/loan-insurance/policies', { params })
  },

  async getLoanPolicies(loanAccountId: number) {
    return apiClient.get<InsurancePolicy[]>(`/loan-insurance/policies/loan/${loanAccountId}`)
  },

  async updatePolicy(id: number, data: Partial<CreatePolicyRequest>) {
    return apiClient.patch<InsurancePolicy>(`/loan-insurance/policies/${id}`, data)
  },

  async renewPolicy(id: number, data: RenewPolicyRequest) {
    return apiClient.post<InsurancePolicy>(`/loan-insurance/policies/${id}/renew`, data)
  },

  async cancelPolicy(id: number, data: CancelPolicyRequest) {
    return apiClient.post<InsurancePolicy>(`/loan-insurance/policies/${id}/cancel`, data)
  },

  // ============================================
  // Premium Payments
  // ============================================

  async createPremiumPayment(data: CreatePremiumPaymentRequest) {
    return apiClient.post<PremiumPayment>('/loan-insurance/premiums', data)
  },

  async updatePremiumPayment(id: number, data: UpdatePremiumPaymentRequest) {
    return apiClient.patch<PremiumPayment>(`/loan-insurance/premiums/${id}`, data)
  },

  async getPolicyPremiums(policyId: number) {
    return apiClient.get<PremiumPayment[]>(`/loan-insurance/premiums/policy/${policyId}`)
  },

  async getOverduePremiums() {
    return apiClient.get<PremiumPayment[]>('/loan-insurance/premiums/overdue')
  },

  // ============================================
  // Expiry & Renewal
  // ============================================

  async getExpiringPolicies(days: number = 30) {
    return apiClient.get(`/loan-insurance/policies/expiring/${days}`)
  },

  async sendRenewalReminder(policyId: number) {
    return apiClient.post(`/loan-insurance/policies/${policyId}/send-renewal-reminder`)
  },

  // ============================================
  // Insurance Claims
  // ============================================

  async createClaim(data: CreateClaimRequest) {
    return apiClient.post<InsuranceClaim>('/loan-insurance/claims', data)
  },

  async getClaim(id: number) {
    return apiClient.get<InsuranceClaim>(`/loan-insurance/claims/${id}`)
  },

  async getClaims(params?: PaginationParams & {
    insurance_policy_id?: number
    loan_account_id?: number
    claim_type?: string
    claim_status?: string
    incident_date_from?: string
    incident_date_to?: string
  }) {
    return apiClient.get<PaginatedResponse<InsuranceClaim>>('/loan-insurance/claims', { params })
  },

  async updateClaim(id: number, data: Partial<CreateClaimRequest>) {
    return apiClient.patch<InsuranceClaim>(`/loan-insurance/claims/${id}`, data)
  },

  async reviewClaim(id: number, data: ReviewClaimRequest) {
    return apiClient.post<InsuranceClaim>(`/loan-insurance/claims/${id}/review`, data)
  },

  async recordClaimPayment(id: number, data: ClaimPaymentRequest) {
    return apiClient.post<InsuranceClaim>(`/loan-insurance/claims/${id}/payment`, data)
  },

  async getPendingClaims() {
    return apiClient.get<InsuranceClaim[]>('/loan-insurance/claims/pending/review')
  },

  // ============================================
  // Bulk Operations
  // ============================================

  async bulkRenewPolicies(data: {
    policy_ids: number[]
    renewal_start_date: string
    renewal_end_date: string
    premium_increase_percentage?: number
    bulk_renewal_reference: string
  }) {
    return apiClient.post('/loan-insurance/bulk/renewal', data)
  },

  async bulkSendRenewalReminders(days: number = 30) {
    return apiClient.post(`/loan-insurance/bulk/send-renewal-reminders?days=${days}`)
  },

  // ============================================
  // Statistics & Dashboard
  // ============================================

  async getStatistics(fromDate?: string, toDate?: string) {
    return apiClient.get<InsuranceStatistics>('/loan-insurance/statistics', {
      params: { from_date: fromDate, to_date: toDate }
    })
  },

  async getDashboard() {
    return apiClient.get('/loan-insurance/dashboard')
  },

  async getCoverageReport() {
    return apiClient.get('/loan-insurance/coverage-report')
  },
}
