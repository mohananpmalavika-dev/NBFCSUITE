/**
 * Loan Restructuring Service
 * API calls for loan restructuring management
 */

import { apiClient } from '@/lib/api-client'
import type { PaginatedResponse, PaginationParams } from '@/types'

export interface LoanRestructuring {
  id: number
  loan_account_id: number
  restructuring_number: string
  restructuring_type: 'emi_reduction' | 'tenure_extension' | 'moratorium' | 'interest_rate_reduction' | 'principal_restructure' | 'hybrid'
  reason: 'financial_hardship' | 'job_loss' | 'medical_emergency' | 'business_loss' | 'natural_disaster' | 'covid_impact' | 'other'
  reason_details: string
  status: 'draft' | 'pending_approval' | 'approved' | 'rejected' | 'implemented' | 'cancelled'
  
  // Current loan details
  current_emi: number
  current_outstanding: number
  current_tenure_remaining: number
  
  // Proposed parameters
  proposed_emi?: number
  proposed_tenure?: number
  proposed_interest_rate?: number
  moratorium_months?: number
  
  // Approved parameters
  approved_emi?: number
  approved_tenure?: number
  approved_interest_rate?: number
  approved_moratorium_months?: number
  
  // Implemented parameters
  final_emi?: number
  final_tenure?: number
  final_interest_rate?: number
  final_outstanding?: number
  
  // Financial details
  customer_income?: number
  customer_obligations?: number
  waiver_amount?: number
  waiver_type?: string
  estimated_loss?: number
  recovery_probability?: number
  
  // Approval/rejection
  approval_remarks?: string
  approved_at?: string
  approved_by?: number
  rejection_reason?: string
  rejected_at?: string
  
  // Implementation
  implementation_date?: string
  first_emi_date?: string
  moratorium_start_date?: string
  moratorium_end_date?: string
  implemented_at?: string
  
  created_at: string
  updated_at: string
}

export interface CreateRestructuringRequest {
  loan_account_id: number
  restructuring_type: string
  reason: string
  reason_details: string
  current_emi: number
  current_outstanding: number
  current_tenure_remaining: number
  proposed_emi?: number
  proposed_tenure?: number
  proposed_interest_rate?: number
  moratorium_months?: number
  customer_income?: number
  customer_obligations?: number
  supporting_documents?: string[]
}

export interface ApproveRestructuringRequest {
  approved_emi?: number
  approved_tenure?: number
  approved_interest_rate?: number
  approved_moratorium_months?: number
  approval_remarks: string
  waiver_amount?: number
  waiver_type?: string
  credit_committee_approval?: boolean
  risk_assessment?: string
  estimated_loss?: number
  recovery_probability?: number
}

export interface RejectRestructuringRequest {
  rejection_reason: string
  alternative_suggestions?: string
  can_reapply?: boolean
  reapply_after_days?: number
}

export interface ImplementRestructuringRequest {
  implementation_date: string
  first_emi_date: string
  final_emi: number
  final_tenure: number
  final_interest_rate: number
  final_outstanding: number
  moratorium_start_date?: string
  moratorium_end_date?: string
  waiver_applied?: number
  implementation_remarks?: string
}

export interface RestructuringStatistics {
  total_requests: number
  pending_requests: number
  approved_requests: number
  rejected_requests: number
  implemented_requests: number
  cancelled_requests: number
  by_type: Record<string, number>
  by_reason: Record<string, number>
  total_waiver_amount: number
  total_estimated_loss: number
  average_waiver_per_case: number
  approval_rate: number
  implementation_rate: number
}

export const restructuringService = {
  // ============================================
  // Restructuring Requests
  // ============================================

  async createRequest(data: CreateRestructuringRequest) {
    return apiClient.post<LoanRestructuring>('/restructuring/requests', data)
  },

  async getRequest(id: number) {
    return apiClient.get<LoanRestructuring>(`/restructuring/requests/${id}`)
  },

  async getRequests(params?: PaginationParams & {
    loan_account_id?: number
    status?: string
    restructuring_type?: string
    reason?: string
    created_from?: string
    created_to?: string
  }) {
    return apiClient.get<PaginatedResponse<LoanRestructuring>>('/restructuring/requests', { params })
  },

  async getLoanRequests(loanAccountId: number) {
    return apiClient.get<LoanRestructuring[]>(`/restructuring/requests/loan/${loanAccountId}`)
  },

  async updateRequest(id: number, data: Partial<CreateRestructuringRequest>) {
    return apiClient.patch<LoanRestructuring>(`/restructuring/requests/${id}`, data)
  },

  // ============================================
  // Approval Workflow
  // ============================================

  async approveRequest(id: number, data: ApproveRestructuringRequest) {
    return apiClient.post<LoanRestructuring>(`/restructuring/requests/${id}/approve`, data)
  },

  async rejectRequest(id: number, data: RejectRestructuringRequest) {
    return apiClient.post<LoanRestructuring>(`/restructuring/requests/${id}/reject`, data)
  },

  async implementRestructuring(id: number, data: ImplementRestructuringRequest) {
    return apiClient.post<LoanRestructuring>(`/restructuring/requests/${id}/implement`, data)
  },

  async cancelRequest(id: number, cancellationReason: string) {
    return apiClient.post<LoanRestructuring>(`/restructuring/requests/${id}/cancel`, {
      cancellation_reason: cancellationReason
    })
  },

  // ============================================
  // Pending Requests
  // ============================================

  async getPendingApprovals() {
    return apiClient.get<LoanRestructuring[]>('/restructuring/requests/pending/approval')
  },

  async getPendingImplementations() {
    return apiClient.get<LoanRestructuring[]>('/restructuring/requests/pending/implementation')
  },

  // ============================================
  // Analysis & Summary
  // ============================================

  async getLoanSummary(loanAccountId: number) {
    return apiClient.get(`/restructuring/summary/loan/${loanAccountId}`)
  },

  async getLoanHistory(loanAccountId: number) {
    return apiClient.get(`/restructuring/history/loan/${loanAccountId}`)
  },

  async analyzeImpact(loanAccountId: number, params: {
    proposed_emi?: number
    proposed_tenure?: number
    proposed_interest_rate?: number
    moratorium_months?: number
  }) {
    return apiClient.post('/restructuring/analysis/impact', {
      loan_account_id: loanAccountId,
      ...params
    })
  },

  // ============================================
  // Statistics
  // ============================================

  async getStatistics(fromDate?: string, toDate?: string) {
    return apiClient.get<RestructuringStatistics>('/restructuring/statistics', {
      params: { from_date: fromDate, to_date: toDate }
    })
  },

  // ============================================
  // Eligibility
  // ============================================

  async checkEligibility(loanAccountId: number) {
    return apiClient.get(`/restructuring/eligibility/loan/${loanAccountId}`)
  },

  // ============================================
  // Bulk Operations
  // ============================================

  async bulkCreate(data: {
    loan_account_ids: number[]
    restructuring_type: string
    reason: string
    reason_details: string
    moratorium_months?: number
    bulk_approval_reference: string
    approved_by_committee?: boolean
    auto_implement?: boolean
  }) {
    return apiClient.post('/restructuring/bulk/create', data)
  },
}
